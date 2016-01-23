-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament

CREATE TABLE players(
	id 		SERIAL PRIMARY KEY,
	name 	TEXT NOT NULL,
	score 	INT NOT NULL DEFAULT 0
);

CREATE TABLE matches(
	id 			SERIAL PRIMARY KEY,
	player1_id	INT NOT NULL REFERENCES players(id),
	player2_id	INT NOT NULL REFERENCES players(id),
	winner_id	INT NOT NULL,
	CONSTRAINT valid_winner CHECK (winner_id = player1_id or winner_id = player2_id)
);

-- after testStandingsBeforeMatches()
ALTER TABLE players RENAME COLUMN score TO win;
ALTER TABLE players ADD COLUMN match INT NOT NULL DEFAULT 0;

--after testReportMatches()
ALTER TABLE matches DROP COLUMN player1_id, DROP COLUMN player2_id;
ALTER TABLE matches ADD COLUMN loser_id INT NOT NULL REFERENCES players(id);
ALTER TABLE matches ADD FOREIGN KEY (winner_id) REFERENCES players(id);

-- after first submission code review
ALTER TABLE matches ADD CONSTRAINT valid_id CHECK (winner_id != loser_id);