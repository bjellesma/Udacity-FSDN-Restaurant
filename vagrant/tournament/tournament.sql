-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;

--matches table
create table matches(
  id serial primary key,
  winner_id integer REFERENCES players(id),
  loser_id integer REFERENCES players(id)
);

--player table
create table players(
  id serial primary key,
  wins smallint DEFAULT 0,
  loses smallint DEFAULT 0,
  matches integer DEFAULT 0,
  name text
);
