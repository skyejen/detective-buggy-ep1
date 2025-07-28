--------------------- suspects table

DROP TABLE IF EXISTS suspects CASCADE;

CREATE TABLE suspects (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    species TEXT,
    alibi TEXT,
    is_guilty BOOLEAN,
    image_filename TEXT
);

INSERT INTO suspects (name, description, species, alibi, is_guilty, image_filename) VALUES
    ('DS Cookie', 'A fiery calico officer with a short temper but a good heart. Loves order, hates moths.', 'Cat', 'Keeping the station safe from airborne threats.', FALSE, 'cookie.webp'),
    ('PC Steven', 'A quiet seagull on CCTV duty. Keeps his answers short, which makes him seem disinterested, but he''s just not one for small talk.', 'Seagull', 'Monitoring the security room feeds.', FALSE, 'steven.webp'),
    ('DS Spoony', 'A smug but usually harmless officer. Has a sharp tongue and a rough past.', 'Spoon', 'Claims to have a chicken allergy.', TRUE, 'spoony.webp'),
    ('PC Noodle', 'Utterly useless but weirdly loveable. Thinks he''s helping. Usually makes things worse. Obsessed with vending machines.', 'Seahorse', 'Nowhere near the crime scene. Hopefully.', FALSE, 'noodle.webp'),
    ('DC Banana', 'A sweet new recruit on probation. Nervous but eager. Looks up to senior officers.', 'Banana', 'Was... missing?', FALSE, 'banana.webp'),
    ('DS Theo', 'Retired from active duty. Known for his calm wisdom and perfect cup of tea. Often found filing evidence with Snakey, his loyal green companion.', 'Dog', 'In the Archives with Snakey, filing evidence.', FALSE, 'theo.webp');


--------------------- evidence table

DROP TABLE IF EXISTS evidence CASCADE;

CREATE TABLE evidence (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL, -- 'clue', 'record', or 'note'
    location TEXT,
    suspect_id INTEGER,
    always_visible BOOLEAN DEFAULT FALSE,
    label TEXT DEFAULT 'Inspect',
    origin TEXT,
    image_filename TEXT,
    FOREIGN KEY (suspect_id) REFERENCES suspects(id)
);

INSERT INTO evidence (name, description, category, location, suspect_id, always_visible, label, origin, image_filename) VALUES
    -- Misc --
    ('Case Notes', 'Buggy was awarded chicken treats by the Chief Constable. They were later found missing from his desk drawer.', 'record', 'Briefing Room', NULL, TRUE, 'TBC', 'Briefing', NULL),
    ('Missing Banana', 'Probationer Banana failed to report for duty today.', 'note', 'Briefing Room', 5, TRUE, 'TBC', 'Briefing', NULL),

    -- Cookie (1) --
    ('Furball', 'A suspicious clump of calico fur found inside Buggy''s desk drawer.', 'clue', 'Crime Scene', 1, FALSE, 'Inspect Furball', 'Crime Scene', 'furball.webp'),
    ('Furball Explanation', 'Cookie claimed she had been chasing a moth before the crime took place.', 'record', 'Interview Room', 1, FALSE, 'TBC', 'Interview with DS Cookie', NULL),

    -- Steven (2) --
    ('Bird Footprints', 'Suspicious bird-like footprints.', 'clue', 'Crime Scene', 2, FALSE, 'Inspect Bird Footprints', 'Crime Scene', 'birdprints.webp'),
    ('CCTV Footage', 'Footage from the time of the crime. Can only be viewed in the Security Room.', 'clue', 'Interview Room', 2, FALSE, 'Play CCTV Footage', 'Interview with PC Steven', 'cctv-footage.webp'),

    -- Spoony (3) --
    ('Chicken Treat Food Allergy', 'Spoony claimed to be allergic to chicken treats.', 'record', 'Interview Room', 3, FALSE, 'TBC', 'Interview with DS Spoony', NULL),
    ('Spoony''s Sunday Shift', 'Claimed that he worked in Records on Sunday. These guys are in another building and don''t have access to my office.', 'record', 'Interview Lobby', 3, FALSE, 'TBC', 'Interview with DS Spoony', NULL),
    ('Stilts With Bird Feet', 'Suspiciously looking stilts. What on earth?', 'clue', 'Security Room', 3, FALSE, 'Inspect Stilts With Bird&nbsp;Feet', 'Security Room Closet', 'stilts.webp'),
    ('Rusty Stain', 'There''s a rust-colored stain inside the Security Room''s closet.', 'clue', 'Security Room', 3, FALSE, 'Inspect Rusty Stain', 'Security Room Closet', 'stain.webp'),
    ('Professor Ball''s Comment', 'Scribbled message: ''Some steal for hunger. Others steal to take away.''', 'note', 'Suspects', 3, FALSE, 'Interact with Professor Ball', 'Suspects', NULL),
    ('Locker Room Access', 'After overhearing PC Noodle grumble, Buggy began to suspect the locker room might be hiding something.', 'note', 'Interview Lobby', 3, FALSE, 'TBC', 'Buggy''s Thoughts', NULL),

    -- Banana (5) --
    ('Sobbing Banana', 'Banana was found tied up in the Security Room''s closet. Shaken and unable to speak, for now.', 'record', 'Security Room', 5, FALSE, 'TBC', 'Security Room Closet', NULL),
    ('Corrupted CCTV Footage', 'Something (or someone) sabotaged the evidence...', 'record', 'Security Room', 5, FALSE, 'TBC', 'Analysed at Security Room', NULL),

    -- Endgame --
    ('Chicken Treats in Spoony''s Locker', 'Inside Spoony''s locker were chicken treats... the same kind Buggy had been awarded.', 'record', 'Locker Room', NULL, FALSE, 'TBC', 'Locker Room', NULL),
    ('Cookie''s Fur in Spoony''s Locker', 'A tuft of calico fur was wedged in the locker door.', 'record', 'Locker Room', NULL, FALSE, 'TBC', 'Locker Room', NULL),
    ('Buggy''s Reflections', 'Is Spoony trying to frame Cookie? Although Cookie is known to cause trouble too. She''s a fantastic officer, but she doesn''t have respect for her superiors. (She did steal my dinner once...)', 'record', 'Locker Room', NULL, FALSE, 'TBC', 'Locker Room', NULL),
    ('Contradictory Alibi', 'Spoony claimed he worked Sunday, but the Records Room was closed.', 'record', 'Interview Lobby', 3, FALSE, 'TBC', 'Overheard PC Noodle', NULL),

    -- Flavour items: Crime Scene
    ('Lost Tennis Ball', 'Buggy sniffed out an old tennis ball. Probably from training days.', 'flavour', 'Crime Scene', NULL, FALSE, 'Sniff Tennis Ball', 'Crime Scene', 'tennis-ball.webp'),
    ('Chewed-Up Report', 'A chewed-up incident report. Must be the new probationer?', 'flavour', 'Crime Scene', NULL, FALSE, 'Inspect Chewed Report', 'Crime Scene', 'police-report.webp'),
    ('Mystery Moth', 'A moth flutters by. Damaged wing?', 'flavour', 'Crime Scene', NULL, FALSE, 'Inspect Moth', 'Crime Scene', 'moth.webp'),

    -- Flavour items: Security Closet
    ('Abandoned Mug', 'A dusty mug with ''World''s Best Pawfficer'' written on it.', 'flavour', 'Security Room Closet', NULL, FALSE, 'Inspect Mug', 'Security Room Closet', 'mug.webp'),
    ('Theo''s Biscuit', 'Dry. Unidentifiable. Still smells tasty. Must be Theo''s.', 'flavour', 'Security Room Closet', NULL, FALSE, 'Inspect Biscuit', 'Security Room Closet', 'biscuit.webp'),
    ('Vending Machine Stickers', 'A vending machine sticker pack. Interesting choice.', 'flavour', 'Security Room Closet', NULL, FALSE, 'Flip through stickers', 'Security Room Closet', 'stickers.webp');


--------------------- dialogues table

DROP TABLE IF EXISTS dialogues CASCADE;

CREATE TABLE dialogues (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    suspect_id INTEGER NOT NULL,
    line TEXT NOT NULL,
    evidence_id INTEGER,
    FOREIGN KEY (suspect_id) REFERENCES suspects(id),
    FOREIGN KEY (evidence_id) REFERENCES evidence(id)
);

INSERT INTO dialogues (suspect_id, line, evidence_id) VALUES

    -- Cookie (1) --
    (1, 'As a police officer, it is my duty to protect the precinct from airborne threats like that moth.', NULL),
    (1, 'I was just doing my job. Who else would do it, if not me?', NULL),
    (1, 'I *do* shed a lot, okay? It''s not a crime.', 4), -- Unlocks clue 'Furball' -> no, this should unlock the potential explanation, so a record, furball clue is in the crime scene

    -- Steven (2) --
    (2, 'I was on shift in the Security room.', NULL),
    (2, 'I''m not sure why you are talking to me before we review the CCTV footage<br>from the time of the crime.', 6), -- Unlocks clue 'CCTV Footage'
    (2, 'I would love to help you, DI Buggy, but I don''t have anything else to say right now.', NULL),

    -- Spoony (3) --
    (3, 'I''m allergic to chicken treats, why would I steal them?', 7), -- Adds a record about chicken allergy
    (3, 'I worked in Records on Sunday. No way I was near the crime scene.', 8), -- Adds a record about the Sunday shift
    (3, 'You call this an interview? This feels more like an interrogation...', NULL),

    -- Noodle (4) --
    (4, 'I wasn''t even at the station. I spent all morning arguing with the vending machine.', NULL),
    (4, 'Wait, was there a crime? I thought we were just on lockdown drill #17.', NULL),
    (4, 'Oh! You said ''crime scene'' and I thought you said ''crime bean'', so I made soup.', NULL),

    -- Banana (5) --
    (5, 'I didn''t mean to do it. I didn''t want to. I was just scared.', NULL),

    -- Theo (6) --
    (6, 'If you ask me, everyone could use a moment of stillness. Even DI Buggy.', NULL),
    (6, 'Every case leaves a mark. But tea and time... they help us process it.', NULL),
    (6, 'Snakey''s idea of cardio is hiding in evidence boxes. I do the running.', NULL);


--------------------- playthroughs table

DROP TABLE IF EXISTS playthroughs CASCADE;

CREATE TABLE IF NOT EXISTS playthroughs (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    timestamp TIMESTAMPTZ NOT NULL,
    player_name TEXT,
    duration_minutes INTEGER,
    accused_name TEXT NOT NULL,
    was_correct BOOLEAN NOT NULL
);
