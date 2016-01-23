-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

create table players(
	id 		serial primary key,
	name 	text not null,
	score 	int not null default 0
);

create table matches(
	id 			serial primary key,
	player1_id	int not null references players(id),
	player2_id	int not null references players(id),
	winner_id	int not null,
	constraint valid_winner check (winner_id = player1_id or winner_id = player2_id)
);

-- after testStandingsBeforeMatches()
alter table players rename column score to win;
alter table players add column match int not null default 0;

--after testReportMatches()
alter table matches drop column player1_id, drop column player2_id;
alter table matches add column loser_id int not null references players(id);
alter table matches add foreign key (winner_id) references players(id);