-- suspects table

DROP TABLE IF EXISTS suspects;

CREATE TABLE suspects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    species TEXT,
    alibi TEXT,
    is_guilty BOOLEAN
);

INSERT INTO suspects (name, species, alibi, is_guilty) VALUES
    ("Cookie", "Cat", "Chasing a moth", 0),
    ("Steven", "Seagull", "Monitoring CCTV", 0),
    ("Spoony", "???", "Claimed allergy to treats", 1);


-- evidence table

DROP TABLE IF EXISTS evidence;

CREATE TABLE evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL, -- 'clue', 'record', or 'note'
    location TEXT,
    suspect_id INTEGER, -- nullable for items not tied to any suspect
    FOREIGN KEY (suspect_id) REFERENCES suspects(id)
);

INSERT INTO clues (name, description, location, suspect_id) VALUES
    ("Furball", "A suspicious clump of calico fur.", "Crime Scene", 1),
    ("Bird Footprints", "Strange bird-like footprints.", "Crime Scene", 2),
    ("Professor Ball", "Professor Ball seems unusually disoriented.", "Crime Scene", NULL),
    ("Hidden Treat Wrapper", "A wrapper hidden behind the evidence board.", "Briefing Room", NULL),
    ("CCTV footage", "CCTV footage from the time of the crime.", "Security Room", 2);


-- suspects' dialogue lines table

DROP TABLE IF EXISTS dialogues;

CREATE TABLE dialogues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    suspect_id INTEGER NOT NULL,
    line TEXT NOT NULL,
    evidence_id INTEGER, -- Optional: unlocks evidence by ID when this line is triggered
    FOREIGN KEY (suspect_id) REFERENCES suspects(id),
    FOREIGN KEY (evidence_id) REFERENCES evidence(id)
);

-- Assuming:
-- Suspect 1 = Cookie
-- Suspect 2 = Steven
-- Suspect 3 = Spoony

INSERT INTO dialogues (suspect_id, line, clue_unlocked_id) VALUES
    (1, 'I was just doing my job. As a police officer, it is my duty to protect the precinct from airborne threats like that moth.', NULL),
    (1, 'I *do* shed a lot, okay? It’s not a crime.', 1), -- Unlocks clue #1: Furball
    (2, 'I was on shift in the Security room', NULL),
    (2, 'I would love to help you, DI Buggy, but I don''t have anything else to say.', NULL),
    (3, 'You call this an interview? This feels more like an interrogation...', NULL),
    (3, 'I''m allergic to chicken treats, why would I steal them?', NULL);
