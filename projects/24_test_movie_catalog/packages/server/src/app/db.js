import fs from 'fs';

import Database from 'better-sqlite3';

import { readJson } from './utils.js';



// https://github.com/WiseLibs/better-sqlite3/blob/HEAD/docs/api.md
export class MovieDatabase {
    #db = null;

    static connect (dbPath, sourcePath) {
        return new MovieDatabase().#setup(dbPath, sourcePath);
    };

    getDB = () => {
        return this.#db;
    };

    disconnect = () => {
        this.#close();
    };

    #setup = (dbPath, sourcePath) => {
        const needToFill = !fs.existsSync(dbPath);

        this.#open(dbPath);

        if (needToFill) {
            console.log('Creating database...');

            this.#createTables();
            this.#fillDatabase(sourcePath);

            console.log('Database has been created successfully');
        }

        return this;
    };

    #open = (dbPath) => {
        this.#db = new Database(dbPath);

        this.#db.pragma('journal_mode = WAL');
        this.#db.pragma('case_sensitive_like = ON');
    };

    #close = (dbPath) => {
        this.#db?.close();
        this.#db = null;
    };

    #createTables = () => {
        const queries = [
            `CREATE TABLE IF NOT EXISTS award_titles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL
            );`,

            `CREATE TABLE IF NOT EXISTS nomination_titles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL
            );`,
            
            `CREATE TABLE IF NOT EXISTS platforms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL
            );`,
            
            `CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_russian TEXT UNIQUE,
                name_foreign TEXT UNIQUE
            );`,
            
            `CREATE TABLE IF NOT EXISTS countries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL
            );`,
            
            `CREATE TABLE IF NOT EXISTS genres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL
            );`,
            
            `CREATE TABLE IF NOT EXISTS releasers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL
            );`,
            
            `CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kp_id INTEGER UNIQUE NOT NULL,
                title_russian TEXT,
                title_foreign TEXT,
                description_short TEXT,
                description_full TEXT,
                slogan TEXT,
                top250_position INTEGER UNIQUE,
                production_year INTEGER,
                age INTEGER,
                premiere_date TEXT,
                duration INTEGER,
                budget_amount INTEGER,
                budget_currency TEXT,
                box_office_amount INTEGER,
                box_office_currency TEXT,
                rating_value REAL DEFAULT 0.0,
                rating_vote_count INTEGER DEFAULT 0
            );`,
            
            `CREATE TABLE IF NOT EXISTS audience (
                movie_id INTEGER NOT NULL,
                country_id INTEGER NOT NULL,
                count INTEGER DEFAULT 0,
                PRIMARY KEY (movie_id, country_id),
                FOREIGN KEY (movie_id) REFERENCES movies(id),
                FOREIGN KEY (country_id) REFERENCES countries(id)
            );`,
            
            `CREATE TABLE IF NOT EXISTS releases (
                movie_id INTEGER NOT NULL,
                releaser_id INTEGER NOT NULL,
                release_type TEXT NOT NULL,
                release_date TEXT NOT NULL,
                PRIMARY KEY (movie_id, releaser_id, release_type),
                FOREIGN KEY (movie_id) REFERENCES movies(id),
                FOREIGN KEY (releaser_id) REFERENCES releasers(id)
            );`,
            
            `CREATE TABLE IF NOT EXISTS awards (
                movie_id INTEGER NOT NULL,
                award_title_id INTEGER NOT NULL,
                nomination_title_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                win INTEGER NOT NULL, 
                PRIMARY KEY (movie_id, award_title_id, nomination_title_id, year),
                FOREIGN KEY (movie_id) REFERENCES movies(id),
                FOREIGN KEY (award_title_id) REFERENCES award_titles(id),
                FOREIGN KEY (nomination_title_id) REFERENCES nomination_titles(id)
            );`,
            
            `CREATE TABLE IF NOT EXISTS watch_urls (
                movie_id INTEGER NOT NULL,
                platform_id INTEGER NOT NULL,
                watch_url TEXT,
                PRIMARY KEY (movie_id, platform_id),
                FOREIGN KEY (movie_id) REFERENCES movies(id),
                FOREIGN KEY (platform_id) REFERENCES platforms(id)
            );`,
            
            `CREATE TABLE IF NOT EXISTS movie_to_genres (
                movie_id INTEGER NOT NULL,
                genre_id INTEGER NOT NULL,
                PRIMARY KEY (movie_id, genre_id),
                FOREIGN KEY (movie_id) REFERENCES movies(id),
                FOREIGN KEY (genre_id) REFERENCES genres(id)
            );`,
            
            `CREATE TABLE IF NOT EXISTS movie_to_countries (
                movie_id INTEGER NOT NULL,
                country_id INTEGER NOT NULL,
                PRIMARY KEY (movie_id, country_id),
                FOREIGN KEY (movie_id) REFERENCES movies(id),
                FOREIGN KEY (country_id) REFERENCES countries(id)
            );`,
            
            `CREATE TABLE IF NOT EXISTS movie_to_actors (
                movie_id INTEGER NOT NULL,
                actor_id INTEGER NOT NULL,
                PRIMARY KEY (movie_id, actor_id),
                FOREIGN KEY (movie_id) REFERENCES movies(id),
                FOREIGN KEY (actor_id) REFERENCES people(id)
            );`,
            
            `CREATE TABLE IF NOT EXISTS movie_to_vo_actors (
                movie_id INTEGER NOT NULL,
                actor_id INTEGER NOT NULL,
                PRIMARY KEY (movie_id, actor_id),
                FOREIGN KEY (movie_id) REFERENCES movies(id),
                FOREIGN KEY (actor_id) REFERENCES people(id)
            );`,
            
            `CREATE TABLE IF NOT EXISTS movie_to_directors (
                movie_id INTEGER NOT NULL,
                director_id INTEGER NOT NULL,
                PRIMARY KEY (movie_id, director_id),
                FOREIGN KEY (movie_id) REFERENCES movies(id),
                FOREIGN KEY (director_id) REFERENCES people(id)
            );`,
            
            `CREATE TABLE IF NOT EXISTS movie_to_writers (
                movie_id INTEGER NOT NULL,
                writer_id INTEGER NOT NULL,
                PRIMARY KEY (movie_id, writer_id),
                FOREIGN KEY (movie_id) REFERENCES movies(id),
                FOREIGN KEY (writer_id) REFERENCES people(id)
            );`,
            
            `CREATE TABLE IF NOT EXISTS movie_to_producers (
                movie_id INTEGER NOT NULL,
                producer_id INTEGER NOT NULL,
                PRIMARY KEY (movie_id, producer_id),
                FOREIGN KEY (movie_id) REFERENCES movies(id),
                FOREIGN KEY (producer_id) REFERENCES people(id)
            );`,
            
            `CREATE TABLE IF NOT EXISTS movie_to_composers (
                movie_id INTEGER NOT NULL,
                composer_id INTEGER NOT NULL,
                PRIMARY KEY (movie_id, composer_id),
                FOREIGN KEY (movie_id) REFERENCES movies(id),
                FOREIGN KEY (composer_id) REFERENCES people(id)
            );`,
            
            `CREATE TABLE IF NOT EXISTS movie_to_designers (
                movie_id INTEGER NOT NULL,
                designer_id INTEGER NOT NULL,
                PRIMARY KEY (movie_id, designer_id),
                FOREIGN KEY (movie_id) REFERENCES movies(id),
                FOREIGN KEY (designer_id) REFERENCES people(id)
            );`,
            
            `CREATE TABLE IF NOT EXISTS movie_to_editors (
                movie_id INTEGER NOT NULL,
                editor_id INTEGER NOT NULL,
                PRIMARY KEY (movie_id, editor_id),
                FOREIGN KEY (movie_id) REFERENCES movies(id),
                FOREIGN KEY (editor_id) REFERENCES people(id)
            );`,

            // --------------------------------

            `CREATE VIRTUAL TABLE fts_movies USING fts5(
                title_russian,
                title_foreign,
                content='movies',
                content_rowid='id'
            );`
        ];

        const createTables = this.#db.transaction(() => {
            queries.forEach(query => this.#db.prepare(query).run());
        });

        createTables();
    };

    #fillDatabase = (sourcePath) => {
        const data = readJson(sourcePath);

        const queries = [];

        data.awardTitles.forEach(({ id, title }) => {
            queries.push([
                'INSERT INTO award_titles (id, title) VALUES (?, ?)',
                id, title
            ]);
        });

        data.nominationTitles.forEach(({ id, title }) => {
            queries.push([
                'INSERT INTO nomination_titles (id, title) VALUES (?, ?)',
                id, title
            ]);
        });

        data.platforms.forEach(({ id, title }) => {
            queries.push([
                'INSERT INTO platforms (id, title) VALUES (?, ?)',
                id, title
            ]);
        });

        data.countries.forEach(({ id, title }) => {
            queries.push([
                'INSERT INTO countries (id, title) VALUES (?, ?)',
                id, title
            ]);
        });

        data.genres.forEach(({ id, title }) => {
            queries.push([
                'INSERT INTO genres (id, title) VALUES (?, ?)',
                id, title
            ]);
        });

        data.releasers.forEach(({ id, title }) => {
            queries.push([
                'INSERT INTO releasers (id, title) VALUES (?, ?)',
                id, title
            ]);
        });

        data.people.forEach(({ id, russianName, foreignName }) => {
            queries.push([
                'INSERT INTO people (id, name_russian, name_foreign) VALUES (?, ?, ?)',
                id, russianName, foreignName
            ]);
        });

        data.movies.forEach((movie) => {
            queries.push([
                `INSERT INTO movies (
                    id,
                    kp_id,
                    title_russian,
                    title_foreign,
                    description_short,
                    description_full,
                    slogan,
                    top250_position,
                    production_year,
                    age,
                    premiere_date,
                    duration,
                    budget_amount,
                    budget_currency,
                    box_office_amount,
                    box_office_currency,
                    rating_value,
                    rating_vote_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                movie.id,
                movie.kpId,
                movie.russianTitle,
                movie.foreignTitle,
                movie.shortDescription,
                movie.fullDescription,
                movie.slogan,
                movie.top250Position,
                movie.productionYear,
                movie.age,
                movie.premiereDate,
                movie.duration,
                movie.budgetAmount,
                movie.budgetCurrency,
                movie.boxOfficeAmount,
                movie.boxOfficeCurrency,
                movie.ratingValue,
                movie.ratingVoteCount,
            ]);
        });

        queries.push([ `INSERT INTO fts_movies (rowid, title_russian, title_foreign) SELECT id, title_russian, title_foreign FROM movies;` ]);

        data.audience.forEach(({ movieId, countryId, count }) => {
            queries.push([
                'INSERT INTO audience (movie_id, country_id, count) VALUES (?, ?, ?)',
                movieId, countryId, count
            ]);
        });

        data.releases.forEach(({ movieId, releaserId, releaseType, releaseDate }) => {
            queries.push([
                'INSERT INTO releases (movie_id, releaser_id, release_type, release_date) VALUES (?, ?, ?, ?)',
                movieId, releaserId, releaseType, releaseDate
            ]);
        });

        data.awards.forEach(({ movieId, awardId, nominationId, year, win }) => {
            queries.push([
                'INSERT INTO awards (movie_id, award_title_id, nomination_title_id, year, win) VALUES (?, ?, ?, ?, ?)',
                movieId, awardId, nominationId, year, Number(win)
            ]);
        });

        data.watchUrls.forEach(({ movieId, platformId, watchUrl }) => {
            queries.push([
                'INSERT INTO watch_urls (movie_id, platform_id, watch_url) VALUES (?, ?, ?)',
                movieId, platformId, watchUrl
            ]);
        });

        data.movieToGenres.forEach(({ movieId, genreId }) => {
            queries.push([
                'INSERT INTO movie_to_genres (movie_id, genre_id) VALUES (?, ?)',
                movieId, genreId
            ]);
        });

        data.movieToCountries.forEach(({ movieId, countryId }) => {
            queries.push([
                'INSERT INTO movie_to_countries (movie_id, country_id) VALUES (?, ?)',
                movieId, countryId
            ]);
        });

        data.movieToActors.forEach(({ movieId, personId }) => {
            queries.push([
                'INSERT INTO movie_to_actors (movie_id, actor_id) VALUES (?, ?)',
                movieId, personId
            ]);
        });

        data.movieToVoiceOverActors.forEach(({ movieId, personId }) => {
            queries.push([
                'INSERT INTO movie_to_vo_actors (movie_id, actor_id) VALUES (?, ?)',
                movieId, personId
            ]);
        });

        data.movieToDirectors.forEach(({ movieId, personId }) => {
            queries.push([
                'INSERT INTO movie_to_directors (movie_id, director_id) VALUES (?, ?)',
                movieId, personId
            ]);
        });

        data.movieToWriters.forEach(({ movieId, personId }) => {
            queries.push([
                'INSERT INTO movie_to_writers (movie_id, writer_id) VALUES (?, ?)',
                movieId, personId
            ]);
        });

        data.movieToProducers.forEach(({ movieId, personId }) => {
            queries.push([
                'INSERT INTO movie_to_producers (movie_id, producer_id) VALUES (?, ?)',
                movieId, personId
            ]);
        });

        data.movieToComposers.forEach(({ movieId, personId }) => {
            queries.push([
                'INSERT INTO movie_to_composers (movie_id, composer_id) VALUES (?, ?)',
                movieId, personId
            ]);
        });

        let dups = [];

        data.movieToDesigners.forEach(({ movieId, personId }) => {
            const key = `${ movieId }_${ personId }`;

            if (!dups.includes(key)) {
                dups.push(key);

                queries.push([
                    'INSERT INTO movie_to_designers (movie_id, designer_id) VALUES (?, ?)',
                    movieId, personId
                ]);
            }
        });

        data.movieToEditors.forEach(({ movieId, personId }) => {
            queries.push([
                'INSERT INTO movie_to_editors (movie_id, editor_id) VALUES (?, ?)',
                movieId, personId
            ]);
        });

        const fillTables = this.#db.transaction(() => {
            queries.forEach(([ query, ...args ]) => {
                this.#db.prepare(query).run(...args)
            });
        });

        fillTables();
    };

    getMovieGenres = (movieId) => {
        return this.#db.prepare(`SELECT g.* FROM genres AS g JOIN movie_to_genres AS mtg ON mtg.genre_id = g.id WHERE mtg.movie_id = ?`).all(movieId);
    };

    getMovieCountries = (movieId) => {
        return this.#db.prepare(`SELECT c.* FROM countries AS c JOIN movie_to_countries AS mtc ON mtc.country_id = c.id WHERE mtc.movie_id = ?`).all(movieId);
    };

    getMovieActors = (movieId) => {
        const items = this.#db.prepare(`SELECT p.* FROM people AS p JOIN movie_to_actors AS mta ON mta.actor_id = p.id WHERE mta.movie_id = ?`).all(movieId);

        return items.map(person => this.#convertPerson(person));
    };

    getMovieVoiceActors = (movieId) => {
        const items = this.#db.prepare(`SELECT p.* FROM people AS p JOIN movie_to_vo_actors AS mta ON mta.actor_id = p.id WHERE mta.movie_id = ?`).all(movieId);

        return items.map(person => this.#convertPerson(person));
    };

    getMovieDirectors = (movieId) => {
        const items = this.#db.prepare(`SELECT p.* FROM people AS p JOIN movie_to_directors AS mtd ON mtd.director_id = p.id WHERE mtd.movie_id = ?`).all(movieId);

        return items.map(person => this.#convertPerson(person));
    };

    getMovieWriters = (movieId) => {
        const items = this.#db.prepare(`SELECT p.* FROM people AS p JOIN movie_to_writers AS mtw ON mtw.writer_id = p.id WHERE mtw.movie_id = ?`).all(movieId);

        return items.map(person => this.#convertPerson(person));
    };

    getMovieProducers = (movieId) => {
        const items = this.#db.prepare(`SELECT p.* FROM people AS p JOIN movie_to_producers AS mtp ON mtp.producer_id = p.id WHERE mtp.movie_id = ?`).all(movieId);

        return items.map(person => this.#convertPerson(person));
    };

    getMovieComposers = (movieId) => {
        const items = this.#db.prepare(`SELECT p.* FROM people AS p JOIN movie_to_composers AS mtc ON mtc.composer_id = p.id WHERE mtc.movie_id = ?`).all(movieId);

        return items.map(person => this.#convertPerson(person));
    };

    getMovieDesigners = (movieId) => {
        const items = this.#db.prepare(`SELECT p.* FROM people AS p JOIN movie_to_designers AS mtd ON mtd.designer_id = p.id WHERE mtd.movie_id = ?`).all(movieId);

        return items.map(person => this.#convertPerson(person));
    };

    getMovieEditors = (movieId) => {
        const items = this.#db.prepare(`SELECT p.* FROM people AS p JOIN movie_to_editors AS mte ON mte.editor_id = p.id WHERE mte.movie_id = ?`).all(movieId);

        return items.map(person => this.#convertPerson(person));
    };

    getMovieAwards = (movieId) => {
        const items = this.#db.prepare(`
            SELECT 
                a.rowid  AS id,
                a.year   AS year,
                at.title AS awardTitle,
                nt.title AS nominationTitle,
                a.win    AS win
            FROM awards AS a
            JOIN award_titles AS at ON a.award_title_id = at.id
            JOIN nomination_titles AS nt ON a.nomination_title_id = nt.id
            WHERE a.movie_id = ?
            ORDER BY a.win DESC
        `).all(movieId);

        return items.map(item => this.#convertAward(item));
    };

    getMoviePlatforms = (movieId, apiOrigin) => {
        const items = this.#db.prepare(`
            SELECT
                p.id         AS id,
                p.title      AS platformTitle,
                wu.watch_url AS watchUrl
            FROM watch_urls AS wu
            JOIN platforms AS p ON wu.platform_id = p.id
            WHERE wu.movie_id = ?
        `).all(movieId);

        return items.map(item => this.#convertPlatform(item, apiOrigin));
    };

    getMovieReleases = (movieId) => {
        return this.#db.prepare(`
            SELECT
                r.rowid        AS id,
                r2.title       AS releaserTitle,
                r.release_type AS type,
                r.release_date AS date
            FROM releases AS r
            JOIN releasers AS r2 ON r.releaser_id = r2.id
            WHERE r.movie_id = ?
        `).all(movieId);
    };

    getMovieAudience = (movieId) => {
        return this.#db.prepare(`
            SELECT
                a.rowid      AS id,
                a.country_id AS countryId,
                c.title      AS countryTitle,
                a.count
            FROM audience AS a
            JOIN countries AS c ON a.country_id = c.id
            WHERE a.movie_id = ?
        `).all(movieId);
    };

    searchMovies = (searchQuery, apiOrigin) => {
        searchQuery = (searchQuery || '').replace(/\s+/g, ' ').trim();

        let movies;

        if (searchQuery) {
            searchQuery = JSON.stringify(searchQuery);

            const query  = `SELECT m.* FROM movies AS m JOIN fts_movies as f ON m.id = f.rowid WHERE fts_movies MATCH ?`;
            const args   = `title_russian:${ searchQuery } OR title_foreign:${ searchQuery }`;

            movies = this.#db.prepare(query).all(args);
        } else {
            movies = this.#db.prepare(`SELECT * FROM movies ORDER BY RANDOM() LIMIT 50`).all();
        }

        movies = movies.map(movie => {
            movie = this.#convertMovie(movie, apiOrigin);

            const genres    = this.getMovieGenres(movie.id);
            const countries = this.getMovieCountries(movie.id);

            return this.#createSearchMovie(movie, genres, countries);
        });

        return movies;
    };

    #createSearchMovie = (movie, genres, countries) => {
        let year = movie.productionYear ?? null;

        if (movie.premiereDate) {
            year = Number(movie.premiereDate.split('-')[0]);
        }

        return {
            id: movie.id,
            title: movie.title.russian || movie.title.foreign,
            age: movie.age,
            year,
            posterUrl: movie.posterUrl,
            genre: genres[0]?.title ?? null,
            country: countries[0]?.title ?? null,
        };
    };

    getBasicMovieData = (movieId, apiOrigin) => {
        movieId = Number(movieId);

        if (!Number.isFinite(movieId) || movieId <= 0) {
            throw new Error(`Incorrect movieId param: ${ movieId }`);
        }

        const movie = this.#db.prepare('SELECT * FROM movies WHERE id = ?').get(movieId);

        if (!movie) {
            throw new Error(`Movie with id ${ movieId } is not found`);
        }

        return this.#convertMovie(movie, apiOrigin);
    };

    getFullMovieData = (movieId, apiOrigin) => {
        const movie = this.getBasicMovieData(movieId, apiOrigin);

        movie.genres      = this.getMovieGenres(movie.id);
        movie.countries   = this.getMovieCountries(movie.id);
        movie.actors      = this.getMovieActors(movie.id);
        movie.voiceActors = this.getMovieVoiceActors(movie.id);
        movie.directors   = this.getMovieDirectors(movie.id);
        movie.writers     = this.getMovieWriters(movie.id);
        movie.producers   = this.getMovieProducers(movie.id);
        movie.composers   = this.getMovieComposers(movie.id);
        movie.designers   = this.getMovieDesigners(movie.id);
        movie.editors     = this.getMovieEditors(movie.id);
        movie.awards      = this.getMovieAwards(movie.id);
        movie.platforms   = this.getMoviePlatforms(movie.id, apiOrigin);
        movie.releases    = this.getMovieReleases(movie.id);
        movie.audience    = this.getMovieAudience(movie.id);

        return movie;

        // movie.genres      = genres;
        // movie.countries   = countries;
        // movie.actors      = actors.map(person => this.#convertPerson(person));
        // movie.voiceActors = voiceActors.map(person => this.#convertPerson(person));
        // movie.directors   = directors.map(person => this.#convertPerson(person));
        // movie.writers     = writers.map(person => this.#convertPerson(person));
        // movie.producers   = producers.map(person => this.#convertPerson(person));
        // movie.composers   = composers.map(person => this.#convertPerson(person));
        // movie.designers   = designers.map(person => this.#convertPerson(person));
        // movie.editors     = editors.map(person => this.#convertPerson(person));
        // movie.awards      = awards.map(award => this.#convertAward(award));
        // movie.platforms   = platforms.map(platform => this.#convertPlatform(platform, apiOrigin));
        // movie.releases    = releases;
        // movie.audience    = audience;

        // const actors      = this.#db.prepare(`SELECT p.* FROM people AS p JOIN movie_to_actors AS mta ON mta.actor_id = p.id WHERE mta.movie_id = ?`).all(movieId);
        // const voiceActors = this.#db.prepare(`SELECT p.* FROM people AS p JOIN movie_to_vo_actors AS mta ON mta.actor_id = p.id WHERE mta.movie_id = ?`).all(movieId);
        // const directors   = this.#db.prepare(`SELECT p.* FROM people AS p JOIN movie_to_directors AS mtd ON mtd.director_id = p.id WHERE mtd.movie_id = ?`).all(movieId);
        // const writers     = this.#db.prepare(`SELECT p.* FROM people AS p JOIN movie_to_writers AS mtw ON mtw.writer_id = p.id WHERE mtw.movie_id = ?`).all(movieId);
        // const producers   = this.#db.prepare(`SELECT p.* FROM people AS p JOIN movie_to_producers AS mtp ON mtp.producer_id = p.id WHERE mtp.movie_id = ?`).all(movieId);
        // const composers   = this.#db.prepare(`SELECT p.* FROM people AS p JOIN movie_to_composers AS mtc ON mtc.composer_id = p.id WHERE mtc.movie_id = ?`).all(movieId);
        // const designers   = this.#db.prepare(`SELECT p.* FROM people AS p JOIN movie_to_designers AS mtd ON mtd.designer_id = p.id WHERE mtd.movie_id = ?`).all(movieId);
        // const editors     = this.#db.prepare(`SELECT p.* FROM people AS p JOIN movie_to_editors AS mte ON mte.editor_id = p.id WHERE mte.movie_id = ?`).all(movieId);
        // const countries   = this.#db.prepare(`SELECT c.* FROM countries AS c JOIN movie_to_countries AS mtc ON mtc.country_id = c.id WHERE mtc.movie_id = ?`).all(movieId);
        // const genres      = this.#db.prepare(`SELECT g.* FROM genres AS g JOIN movie_to_genres AS mtg ON mtg.genre_id = g.id WHERE mtg.movie_id = ?`).all(movieId);

        // const awards = this.#db.prepare(`
        //     SELECT 
        //         a.rowid  AS id,
        //         a.year   AS year,
        //         at.title AS awardTitle,
        //         nt.title AS nominationTitle,
        //         a.win    AS win
        //     FROM awards AS a
        //     JOIN award_titles AS at ON a.award_title_id = at.id
        //     JOIN nomination_titles AS nt ON a.nomination_title_id = nt.id
        //     WHERE a.movie_id = ?
        // `).all(movieId);

        // const platforms = this.#db.prepare(`
        //     SELECT
        //         p.id         AS id,
        //         p.title      AS platformTitle,
        //         wu.watch_url AS watchUrl
        //     FROM watch_urls AS wu
        //     JOIN platforms AS p ON wu.platform_id = p.id
        //     WHERE wu.movie_id = ?
        // `).all(movieId);

        // const releases = this.#db.prepare(`
        //     SELECT
        //         r.rowid        AS id,
        //         r2.title       AS releaserTitle,
        //         r.release_type AS type,
        //         r.release_date AS date
        //     FROM releases AS r
        //     JOIN releasers AS r2 ON r.releaser_id = r2.id
        //     WHERE r.movie_id = ?
        // `).all(movieId);

        // const audience = this.#db.prepare(`
        //     SELECT
        //         a.rowid      AS id,
        //         a.country_id AS countryId,
        //         c.title      AS countryTitle,
        //         a.count
        //     FROM audience AS a
        //     JOIN countries AS c ON a.country_id = c.id
        //     WHERE a.movie_id = ?
        // `).all(movieId);

        // ---------------------

        // movie = this.#convertMovie(movie, apiOrigin);

        // movie.actors      = actors.map(person => this.#convertPerson(person));
        // movie.voiceActors = voiceActors.map(person => this.#convertPerson(person));
        // movie.directors   = directors.map(person => this.#convertPerson(person));
        // movie.writers     = writers.map(person => this.#convertPerson(person));
        // movie.producers   = producers.map(person => this.#convertPerson(person));
        // movie.composers   = composers.map(person => this.#convertPerson(person));
        // movie.designers   = designers.map(person => this.#convertPerson(person));
        // movie.editors     = editors.map(person => this.#convertPerson(person));

        // movie.countries   = countries;
        // movie.genres      = genres;

        // movie.awards      = awards.map(award => this.#convertAward(award));
        // movie.platforms   = platforms.map(platform => this.#convertPlatform(platform, apiOrigin));

        // movie.releases    = releases;
        // movie.audience    = audience;

        // return movie;
    };

    #convertMovie = (movie, apiOrigin) => {
        return {
            id: movie.id,
            kpId: movie.kp_id,
            kpUrl: `https://kinopoisk.ru/film/${ movie.kp_id }/`,
            title: this.#convertTitle(movie),
            slogan: movie.slogan,
            age: movie.age,
            duration: movie.duration,
            productionYear: movie.production_year,
            premiereDate: movie.premiere_date,
            description: {
                short: movie.description_short,
                full: movie.description_full
            },
            budget: {
                amount: movie.budget_amount,
                currency: movie.budget_currency
            },
            boxOffice: {
                amount: movie.box_office_amount,
                currency: movie.box_office_currency
            },
            rating: {
                value: movie.rating_value,
                voteCount: movie.rating_vote_count,
                top250Position: movie.top250_position
            },
            posterUrl: `${ apiOrigin }images/posters/${ movie.id }.webp`
        };
    };

    #convertTitle = (item) => {
        return {
            russian: item.title_russian,
            foreign: item.title_foreign,
        };
    };

    #convertPerson = (person) => {
        person.name = {
            russian: person.name_russian,
            foreign: person.name_foreign,
        };

        delete person.name_russian;
        delete person.name_foreign;

        return person;
    };

    #convertAward = (award) => {
        award.win = !!award.win;

        return award;
    };

    #convertPlatform = (platform, apiOrigin) => {
        platform.logoUrl = `${ apiOrigin }images/platforms/${ platform.id }.webp`;

        return platform;
    };
}