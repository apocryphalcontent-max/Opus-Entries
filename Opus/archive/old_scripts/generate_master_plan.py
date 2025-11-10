"""
Generate complete 12,000-entry master plan for Opus Maximus generation
Organized by tier and category with proper priority distribution.

This script creates the 'ENTRY_GENERATION_QUEUE.json' file, which is
used by the 'run_codex_generation.py' orchestrator.

Usage:
    python generate_master_plan.py
"""

import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
OUTPUT_JSON_FILE = Path("ENTRY_GENERATION_QUEUE.json")
# ---

def generate_complete_queue():
    """Generate 12,000 entry specifications"""

    queue = []

    # TIER S+ (Ultra Sophisticated Biblical/Theological) - 500 entries
    tier_splus_biblical = [
        "The Book of Revelation", "The Gospel of John", "The Book of Genesis",
        "The Book of Exodus", "The Book of Isaiah", "The Psalms",
        "The Sermon on the Mount", "The Passion Narrative", "The Resurrection Appearances",
        "The Transfiguration", "The Last Supper", "Gethsemane",
        "The Crucifixion", "The Empty Tomb", "The Road to Emmaus",
        "The Ascension", "Pentecost", "The Olivet Discourse",
        "The Beatitudes", "The Lord's Prayer", "The Parables of Jesus",
        "The Apocalypse of John", "The Vision of Ezekiel", "Jacob's Ladder",
        "The Burning Bush", "The Ten Commandments", "The Ark of the Covenant",
        "The Temple of Solomon", "The Davidic Covenant", "The Abrahamic Covenant",
        "The Mosaic Covenant", "The New Covenant", "The Suffering Servant",
        "The Son of Man", "The Logos Incarnate", "The Alpha and Omega",
        "The Lamb of God", "The Good Shepherd", "The Vine and Branches",
        "The Bread of Life", "The Light of the World", "The Way Truth Life",
        "The True Vine", "The Door of the Sheep", "The Resurrection and Life",
        "I AM Sayings", "The Seven Churches", "The Seven Seals",
        "The Seven Trumpets", "The Woman Clothed with Sun", "The Great Dragon"
    ]

    tier_splus_theological = [
        "The Holy Trinity", "The Hypostatic Union", "Divine Energies vs Essence",
        "The Incarnation", "The Resurrection of the Dead", "Theosis and Deification",
        "The Divine Liturgy", "The Parousia", "Creation Ex Nihilo",
        "The Fall and Original Sin", "The Atonement", "Providence and Free Will",
        "Divine Simplicity", "Divine Impassibility", "The Beatific Vision",
        "Apophatic Theology", "Kataphatic Theology", "Perichoresis",
        "Christus Victor", "Recapitulation", "The Communicatio Idiomatum",
        "The Anhypostasia and Enhypostasia", "Filioque Controversy", "Hesychasm",
        "The Jesus Prayer", "Theoria and Praxis", "Nepsis and Sobriety",
        "Apatheia and Dispassion", "Logoi and Logos", "Essence and Energies",
        "Created and Uncreated Light", "The Taboric Light", "Mystical Theology",
        "The Cloud of Unknowing", "Via Negativa", "The Divine Dark",
        "Infinity and Eternity", "Time and Temporality", "Eschatology",
        "Particular Judgment", "General Judgment", "Heaven and Paradise",
        "Hell and Gehenna", "Purgatory Debate", "Aerial Tollhouses",
        "The Intermediate State", "The Resurrection Body", "The New Jerusalem"
    ]

    for subject in tier_splus_biblical:
        queue.append({"subject": subject, "tier": "S+", "category": "Biblical"})
    
    # Fill remaining S+ up to 250
    for i in range(len(tier_splus_biblical), 250):
        queue.append({"subject": f"Tier S+ Biblical Subject {i+1}", "tier": "S+", "category": "Biblical"})

    for subject in tier_splus_theological:
        queue.append({"subject": subject, "tier": "S+", "category": "Theological"})

    # Fill remaining S+ up to 250
    for i in range(len(tier_splus_theological), 250):
        queue.append({"subject": f"Tier S+ Theological Subject {i+1}", "tier": "S+", "category": "Theological"})


    # TIER S (Ultra Sophisticated Secular) - 1500 entries
    tier_s_mathematics = [
        "Peter Scholze", "Grigori Perelman", "Kurt Gödel", "Terence Tao", "Andrew Wiles", "Alexander Grothendieck",
        "Évariste Galois", "Georg Cantor", "Srinivasa Ramanujan", "Emmy Noether",
        "Leonhard Euler", "Bernhard Riemann", "David Hilbert", "Henri Poincaré",
        "John von Neumann", "Alain Connes", "Michael Atiyah", "Shing-Tung Yau",
        "William Thurston", "Vladimir Arnold", "Andrey Kolmogorov", "Carl Friedrich Gauss",
        "Pierre de Fermat", "René Descartes", "Gottfried Leibniz", "Joseph-Louis Lagrange", "Pierre-Simon Laplace",
        "Augustin-Louis Cauchy", "Niels Henrik Abel", "Carl Jacobi",
        "William Hamilton", "Arthur Cayley", "James Sylvester", "Felix Klein",
        "Sophus Lie", "Hermann Minkowski", "Stefan Banach", "John Nash", "Paul Erdős", "Jean-Pierre Serre",
        "Yuri Manin", "Pierre Deligne", "Maxim Kontsevich", "Maryam Mirzakhani",
        "Manjul Bhargava", "Jacob Lurie", "Ben Green"
    ] # Note: Blaise Pascal, Isaac Newton are in Science

    tier_s_physics = [
        "Edward Witten", "Albert Einstein", "Stephen Hawking", "Roger Penrose", "Werner Heisenberg",
        "Niels Bohr", "Paul Dirac", "Richard Feynman", "Max Planck",
        "Erwin Schrödinger", "Ludwig Boltzmann", "John Bell", "Freeman Dyson", "Murray Gell-Mann", "Steven Weinberg",
        "Abdus Salam", "Sheldon Glashow", "Gerard 't Hooft", "Frank Wilczek",
        "David Gross", "Juan Maldacena", "Nima Arkani-Hamed", "Cumrun Vafa",
        "Brian Greene", "Leonard Susskind", "Andrei Linde", "Alan Guth",
        "Kip Thorne", "Rainer Weiss", "Barry Barish", "Max Tegmark",
        "Sean Carroll", "Carlo Rovelli", "Lee Smolin", "Abhay Ashtekar"
    ] # Note: James Clerk Maxwell, Isaac Newton are in Science

    tier_s_philosophy = [
        "Georg Wilhelm Friedrich Hegel", "Immanuel Kant", "Søren Kierkegaard", "Friedrich Nietzsche",
        "Martin Heidegger", "Ludwig Wittgenstein", "Edmund Husserl", "Jean-Paul Sartre",
        "Maurice Merleau-Ponty", "Emmanuel Levinas", "Jacques Derrida", "Michel Foucault",
        "Plato", "Aristotle", "Plotinus", "Duns Scotus", "William of Ockham", "Baruch Spinoza",
        "John Locke", "David Hume", "George Berkeley",
        "Johann Fichte", "Friedrich Schelling", "Arthur Schopenhauer",
        "John Stuart Mill", "Charles Sanders Peirce", "William James",
        "Henri Bergson", "Alfred North Whitehead", "Bertrand Russell",
        "G.E. Moore", "Martin Buber", "Karl Jaspers", "Gabriel Marcel",
        "Paul Ricoeur", "Hans-Georg Gadamer", "Jürgen Habermas", "Charles Taylor",
        "Alasdair MacIntyre", "Alvin Plantinga", "Richard Swinburne", "William Lane Craig"
    ] # Note: St. Augustine, St. Thomas Aquinas are in Theology

    for subject in tier_s_mathematics:
        queue.append({"subject": subject, "tier": "S", "category": "Mathematics"})
    for i in range(len(tier_s_mathematics), 500):
        queue.append({"subject": f"Tier S Mathematics Subject {i+1}", "tier": "S", "category": "Mathematics"})
        
    for subject in tier_s_physics:
        queue.append({"subject": subject, "tier": "S", "category": "Physics"})
    for i in range(len(tier_s_physics), 500):
        queue.append({"subject": f"Tier S Physics Subject {i+1}", "tier": "S", "category": "Physics"})

    for subject in tier_s_philosophy:
        queue.append({"subject": subject, "tier": "S", "category": "Philosophy"})
    for i in range(len(tier_s_philosophy), 500):
        queue.append({"subject": f"Tier S Philosophy Subject {i+1}", "tier": "S", "category": "Philosophy"})

    # TIER B (Essential Biblical/Patristic) - 2000 entries
    tier_b_biblical = [
        "St. Paul the Apostle", "St. Peter the Apostle", "St. John the Apostle",
        "St. James the Just", "St. Andrew", "St. Philip", "St. Bartholomew",
        "St. Thomas the Apostle", "St. Matthew", "St. James son of Alphaeus",
        "St. Jude Thaddeus", "St. Simon the Zealot", "St. Matthias",
        "St. Barnabas", "St. Timothy", "St. Titus", "St. Mark the Evangelist",
        "St. Luke the Evangelist", "St. Stephen Protomartyr", "St. Philip the Deacon",
        "The Prophet Isaiah", "The Prophet Jeremiah", "The Prophet Ezekiel",
        "The Prophet Daniel", "The Prophet Hosea", "The Prophet Joel",
        "The Prophet Amos", "The Prophet Obadiah", "The Prophet Jonah",
        "The Prophet Micah", "The Prophet Nahum", "The Prophet Habakkuk",
        "The Prophet Zephaniah", "The Prophet Haggai", "The Prophet Zechariah",
        "The Prophet Malachi", "King David", "King Solomon", "Moses",
        "Abraham", "Isaac", "Jacob", "Joseph the Patriarch", "Job",
        "Noah", "Enoch", "Elijah", "Elisha", "Samuel", "Deborah",
        "Mary Theotokos", "Mary Magdalene", "Mary and Martha of Bethany",
        "The Virgin Mary's Dormition", "Joseph the Betrothed", "Joachim and Anna",
        "St. John the Baptist", "Zachariah and Elizabeth", "Simeon the Righteous",
        "Anna the Prophetess", "The Magi", "The Shepherds at Bethlehem"
    ]

    tier_b_patristic = [
        "St. Maximus the Confessor", "St. Gregory Palamas", "St. John Damascene",
        "St. Isaac the Syrian", "St. Symeon the New Theologian", "St. Athanasius",
        "St. Basil the Great", "St. Gregory of Nyssa", "St. Gregory of Nazianzus",
        "St. John Chrysostom", "St. Cyril of Alexandria", "St. Irenaeus of Lyons",
        "St. Ignatius of Antioch", "St. Polycarp", "St. Clement of Rome",
        "St. Justin Martyr", "St. Cyprian of Carthage", "St. Hippolytus of Rome",
        "St. Ephrem the Syrian", "St. Cyril of Jerusalem", "St. Hilary of Poitiers",
        "St. Ambrose of Milan", "St. Jerome", "St. Augustine of Hippo",
        "St. Leo the Great", "St. Gregory the Great", "St. Bede the Venerable",
        "St. Theodore the Studite", "St. Photios the Great", "St. Romanos the Melodist",
        "St. Andrew of Crete", "St. John Climacus", "St. Mark the Ascetic",
        "St. Diadochus of Photiki", "St. Hesychius of Jerusalem", "Evagrius Ponticus",
        "St. Macarius the Great", "St. Anthony the Great", "St. Pachomius",
        "St. Shenoute", "St. Benedict", "St. Columba", "St. Patrick"
    ] # Note: Augustine is also in Theology golden corpus

    for subject in tier_b_biblical:
        queue.append({"subject": subject, "tier": "B", "category": "Biblical"})
    for i in range(len(tier_b_biblical), 1000):
        queue.append({"subject": f"Tier B Biblical Subject {i+1}", "tier": "B", "category": "Biblical"})

    for subject in tier_b_patristic:
        queue.append({"subject": subject, "tier": "B", "category": "Patristic"})
    for i in range(len(tier_b_patristic), 1000):
        queue.append({"subject": f"Tier B Patristic Subject {i+1}", "tier": "B", "category": "Patristic"})

    # TIER A (Essential Sophisticated) - 3000 entries
    tier_a_literature = [
        "Fyodor Dostoevsky", "Leo Tolstoy", "Dante Alighieri", "John Milton",
        "William Shakespeare", "T.S. Eliot", "C.S. Lewis", "J.R.R. Tolkien",
        "Flannery O'Connor", "Gerard Manley Hopkins", "George Herbert",
        "John Donne", "Alexander Solzhenitsyn", "Nikolai Gogol", "Anton Chekhov",
        "Ivan Turgenev", "Mikhail Lermontov", "Alexander Pushkin", "Boris Pasternak",
        "Osip Mandelstam", "Anna Akhmatova", "Marina Tsvetaeva", "Vladimir Nabokov",
        "Jorge Luis Borges", "Gabriel García Márquez", "Octavio Paz", "Pablo Neruda",
        "Rainer Maria Rilke", "Paul Celan", "Friedrich Hölderlin", "Johann Goethe",
        "Franz Kafka", "Thomas Mann", "Hermann Hesse", "Robert Musil",
        "Samuel Beckett", "James Joyce", "Virginia Woolf", "W.B. Yeats",
        "Seamus Heaney", "Derek Walcott", "Czesław Miłosz", "Wisława Szymborska"
    ]

    tier_a_science = [
        "Gregor Mendel", "Charles Darwin", "Francis Crick", "James Watson",
        "Rosalind Franklin", "Barbara McClintock", "Louis Pasteur", "Marie Curie",
        "Pierre Curie", "Dmitri Mendeleev", "Linus Pauling", "Carl Linnaeus",
        "Galileo Galilei", "Johannes Kepler", "Tycho Brahe", "Nicolaus Copernicus",
        "William Harvey", "Robert Hooke", "Antoine Lavoisier", "Jöns Jacob Berzelius",
        "John Dalton", "Michael Faraday", "Joseph Priestley", "Humphry Davy",
        "Robert Boyle", "Niels Henrik David Bohr", "Max Born", "Wolfgang Pauli",
        "Enrico Fermi", "J. Robert Oppenheimer", "Hans Bethe", "Eugene Wigner",
        "John Bardeen", "William Shockley", "Walter Brattain", "Claude Shannon",
        "Alan Turing", "Norbert Wiener"
    ] # Note: Key scientists are already in golden corpus

    for subject in tier_a_literature:
        queue.append({"subject": subject, "tier": "A", "category": "Literature"})
    for i in range(len(tier_a_literature), 1000):
        queue.append({"subject": f"Tier A Literature Subject {i+1}", "tier": "A", "category": "Literature"})

    for subject in tier_a_science:
        queue.append({"subject": subject, "tier": "A", "category": "Science"})
    for i in range(len(tier_a_science), 1000):
        queue.append({"subject": f"Tier A Science Subject {i+1}", "tier": "A", "category": "Science"})

    # Distribute remaining 1000 to tier A
    for i in range(1000):
        queue.append({"subject": f"Tier A Supplementary Subject {i+1}", "tier": "A", "category": "Mixed"})

    # TIER C (Supplementary) - 5000 entries
    for i in range(5000):
        category = ["Philosophy", "Literature", "Science", "History", "Art"][i % 5]
        queue.append({"subject": f"Tier C Subject {i+1}", "tier": "C", "category": category})

    logger.info(f"Total queue size generated: {len(queue)}")
    logger.info(f"Tier S+: {sum(1 for e in queue if e['tier'] == 'S+')}")
    logger.info(f"Tier S: {sum(1 for e in queue if e['tier'] == 'S')}")
    logger.info(f"Tier B: {sum(1 for e in queue if e['tier'] == 'B')}")
    logger.info(f"Tier A: {sum(1 for e in queue if e['tier'] == 'A')}")
    logger.info(f"Tier C: {sum(1 for e in queue if e['tier'] == 'C')}")

    return queue


if __name__ == "__main__":
    logger.info("Starting master plan generation...")
    queue = generate_complete_queue()

    # Save to JSON in the *local directory*
    try:
        with open(OUTPUT_JSON_FILE, 'wb') as f:
            f.write(json.dumps(queue, indent=2).encode('utf-8'))
        
        logger.info(f"✓ Saved {len(queue)} entries to {OUTPUT_JSON_FILE.resolve()}")
    except Exception as e:
        logger.error(f"Failed to save master plan to {OUTPUT_JSON_FILE.resolve()}: {e}")
