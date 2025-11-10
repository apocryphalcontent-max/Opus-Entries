# FILE 26: TERRAFORM INFRASTRUCTURE
# ==================================
# Infrastructure-as-Code (IaC) for deploying Opus Maximus on AWS.
# Production-grade terraform configuration (Combined into single file for distribution).
# File 16 of 20: Infrastructure (Terraform)

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket         = "opus-maximus-terraform-state"
    key            = "opus/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "opus-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "Opus Maximus"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# ============================================================================
# VARIABLES
# ============================================================================
variable "aws_region" {
  type        = string
  default     = "us-west-2"
  description = "AWS region"
}

variable "environment" {
  type        = string
  default     = "production"
  description = "Environment name"
}

variable "cluster_name" {
  type        = string
  default     = "opus-maximus-cluster"
  description = "EKS cluster name"
}

variable "cluster_version" {
  type        = string
  default     = "1.28"
  description = "Kubernetes version"
}

variable "node_count" {
  type        = number
  default     = 3
  description = "Number of worker nodes"
}

variable "instance_type" {
  type        = string
  default     = "g4dn.2xlarge" # GPU instance (NVIDIA T4) optimized for ML inference
  description = "EC2 instance type (GPU)"
}

variable "db_username" {
  type        = string
  default     = "opus_admin"
  sensitive   = true
  description = "RDS master username"
}

# ============================================================================
# DATA SOURCES
# ============================================================================
data "aws_caller_identity" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}

# ============================================================================
# VPC - NETWORKING
# ============================================================================
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = {
    Name = "opus-vpc"
  }
}

resource "aws_subnet" "private" {
  count             = 3
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags = {
    Name                                        = "opus-private-subnet-${count.index + 1}"
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"           = "1"
  }
}

resource "aws_subnet" "public" {
  count                   = 3
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 10}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  tags = {
    Name                                        = "opus-public-subnet-${count.index + 1}"
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                    = "1"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "opus-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  tags = {
    Name = "opus-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = 3
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# NAT Gateway for private subnets (simplified: 1 NAT GW for cost savings in this example)
resource "aws_eip" "nat" {
  domain = "vpc"
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id
  tags = {
    Name = "opus-nat-gw"
  }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }
  tags = {
    Name = "opus-private-rt"
  }
}

resource "aws_route_table_association" "private" {
  count          = 3
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

# ============================================================================
# EKS - KUBERNETES CLUSTER
# ============================================================================
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name                   = var.cluster_name
  cluster_version                = var.cluster_version
  cluster_endpoint_public_access = true
  
  vpc_id     = aws_vpc.main.id
  subnet_ids = aws_subnet.private[*].id

  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    # Essential for GPU nodes
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }

  # Managed Node Groups
  eks_managed_node_groups = {
    # GPU Node Group for Inference
    gpu = {
      name           = "gpu-nodes"
      instance_types = [var.instance_type]
      min_size       = 1
      max_size       = var.node_count
      desired_size   = var.node_count
      
      # Ensure enough disk space for large models (GGUF files)
      disk_size      = 200
      
      labels = {
        accelerator = "nvidia-gpu"
        workload    = "inference"
      }
      
      # Taints to prevent non-GPU workloads from scheduling here by default
      taints = {
        dedicated = {
          key    = "accelerator"
          value  = "nvidia-gpu"
          effect = "PREFER_NO_SCHEDULE"
        }
      }
    }
    # General purpose node group for smaller pods (monitoring, DBs if embedded)
    general = {
      name           = "general-nodes"
      instance_types = ["t3.xlarge"]
      min_size       = 2
      max_size       = 4
      desired_size   = 2
      disk_size      = 50
    }
  }

  # IAM Access
  manage_aws_auth_configmap = true
}

# ============================================================================
# RDS - POSTGRESQL DATABASE
# ============================================================================
resource "random_password" "db_password" {
  length  = 32
  special = false # Simplified for broader compatibility
}

resource "aws_db_subnet_group" "opus" {
  name       = "opus-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id
  tags = {
    Name = "opus-db-subnet-group"
  }
}

resource "aws_security_group" "rds" {
  name        = "opus-rds-sg"
  description = "Allow inbound from EKS"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    cidr_blocks     = [aws_vpc.main.cidr_block]
  }
}

resource "aws_rds_cluster" "opus" {
  cluster_identifier      = "opus-cluster"
  engine                  = "aurora-postgresql"
  engine_mode             = "provisioned"
  engine_version          = "15.4"
  database_name           = "opus"
  master_username         = var.db_username
  master_password         = random_password.db_password.result
  db_subnet_group_name    = aws_db_subnet_group.opus.name
  vpc_security_group_ids  = [aws_security_group.rds.id]
  skip_final_snapshot     = true # For dev/example; set false for prod
  storage_encrypted       = true
  
  serverlessv2_scaling_configuration {
    max_capacity = 16.0
    min_capacity = 0.5
  }

  tags = {
    Name = "opus-rds"
  }
}

resource "aws_rds_cluster_instance" "opus" {
  cluster_identifier = aws_rds_cluster.opus.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.opus.engine
  engine_version     = aws_rds_cluster.opus.engine_version
}

# ============================================================================
# S3 - STORAGE (Entries & Corpus)
# ============================================================================
resource "aws_s3_bucket" "opus_entries" {
  bucket = "opus-maximus-entries-${data.aws_caller_identity.current.account_id}"
  tags = {
    Name = "opus-entries"
  }
}

resource "aws_s3_bucket_versioning" "opus_entries" {
  bucket = aws_s3_bucket.opus_entries.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "opus_entries" {
  bucket = aws_s3_bucket.opus_entries.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "opus_entries" {
  bucket = aws_s3_bucket.opus_entries.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ============================================================================
# OUTPUTS
# ============================================================================
output "cluster_endpoint" {
  value       = module.eks.cluster_endpoint
  description = "EKS cluster endpoint"
}

output "cluster_name" {
  value       = module.eks.cluster_name
  description = "EKS cluster name"
}

output "s3_bucket_entries" {
  value       = aws_s3_bucket.opus_entries.bucket
  description = "S3 bucket for entries"
}

output "rds_endpoint" {
  value       = aws_rds_cluster.opus.endpoint
  description = "RDS cluster endpoint"
}

output "rds_master_password" {
  value       = random_password.db_password.result
  sensitive   = true
  description = "RDS master password (sensitive)"
}

output "configure_kubectl" {
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${var.cluster_name}"
  description = "Command to configure kubectl"
}