import os from 'os';

import cors from 'cors';
import express from 'express';

import { MovieDatabase } from './db.js';



export class Server {
    #config  = null;
    #app     = null;
    #db      = null;
    #port    = null;

    static run (config) {
        return new Server().#setup(config);
    }

    #setup = (config) => {
        this.#setupConfig(config);
        this.#setupDatabase(config);
        this.#setupEndpoints();
    }

    #setupConfig = (config) => {
        this.#config = config;
    };

    #setupDatabase = (config) => {
        // TODO: change paths (?)
        this.#db = MovieDatabase.connect(config.moviesDBPath, config.moviesJsonPath);
    };

    #disconnectDatabase = () => {
        this.#db?.disconnect();
        this.#db = null;
    };

    #shutdown = (server) => {
        server.closeAllConnections();
        server.close(() => {
            console.log('Stopping...');
            this.#disconnectDatabase();
            process.exit(0);
        });
    };

    #onSearch = (req, res) => {
        try {            
            const movies = this.#db.searchMovies(req.query.query, this.#getAPIOrigin(req));
            console.log(this.#getAPIOrigin(req));

            res.json(movies);
        } catch (e) {
            console.log(e);

            res.status(500).send();
        }
    };

    #onGetMovie = async (req, res) => {
        try {            
            const movie = this.#db.getFullMovieData(req.params.id, this.#getAPIOrigin(req));

            // setTimeout(() => res.json(movie), 50000);
            // res.status(500).send();
            res.json(movie);
        } catch (e) {
            console.log(e);  

            res.status(500).send();
        }
    };

    #onNotFound = (req, res) => {
        res.status(404).json({
            data: null,
            error: {
                message: 'Endpoint is not found'
            }
        });
    };

    #getAPIOrigin = (req) => {
        return `${ req.protocol }://${ req.ip }:${ this.#port }/`;
    };

    #showListeningIPs = ({ address, port }) => {
        const interfaces  = os.networkInterfaces();
        const internalIPs = new Set();
        const externalIPs = new Set();

        if (address === '0.0.0.0') {
            for (const interfaceName in interfaces) {
                for (const net of interfaces[interfaceName]) {
                    if (net.family !== 'IPv4') {
                        continue;
                    }

                    const listeningAddress = `${ net.address }:${ port }`;

                    if (net.internal) {
                        internalIPs.add(listeningAddress);
                    } else {
                        externalIPs.add(listeningAddress);                        
                    }
                }
            }
        } else {
            listeningIPs.add(address);
        }

        const listeningIP = [
            ...internalIPs,
            ...externalIPs,
        ];

        console.log(`Server running on:`);

        listeningIP.forEach((listeningAddress) => {
            console.log(`- ${ listeningAddress }`);
        });
    };

    #setupEndpoints = () => {
        const { host, port } = this.#config;

        this.#app = express();

        this.#app.use(cors());
        this.#app.use(express.json());
        this.#app.use(express.static(this.#config.staticPath));

        this.#app.get('/api/movies/search', this.#onSearch);
        this.#app.get('/api/movie/:id', this.#onGetMovie);

        this.#app.use(this.#onNotFound);

        const server = this.#app.listen(port, host, () => {
            const address = server.address();

            this.#port = address.port;

            this.#showListeningIPs(address);
        });

        process.on('SIGINT', () => this.#shutdown(server));
        process.on('SIGTERM', () => this.#shutdown(server));
        process.on('SIGBREAK', () => this.#shutdown(server));
    };
}