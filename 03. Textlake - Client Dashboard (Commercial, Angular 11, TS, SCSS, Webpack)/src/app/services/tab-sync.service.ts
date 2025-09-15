type Action<TArgs extends any[]> = Func<TArgs, void>;

type Mechanism = "storagesync" | "cookiesync" | "serversync";

const enum LogLevel {
    DEBUG = "DEBUG",
    INFO = "INFO",
    WARN = "WARN",
    ERROR = "ERROR"
}

interface Logger {
    debug (message : string) : void;
    info (message : string) : void;
    warn (message : string) : void;
    error (message : string) : void;
}

interface FallbackOptions {
    pollFrequency : number;
    path : string;
    secure : boolean;
    httpOnly : boolean;
}

interface Config {
    channel : string;
    level? : LogLevel;
    fallback? : Partial<FallbackOptions>;
}

interface Options {
    channel : string;
    level : LogLevel;
    fallback : FallbackOptions;
}

interface Context {
    options : Options;
    logger : Logger;
    mechanism : Mechanism;
    isFallback : boolean;
    isServer : boolean;
}

interface Controller {
    start : () => void;
    stop : () => void;
    trigger : () => void;
    isRunning : boolean;
    mechanism : Mechanism;
    isFallback : boolean;
    isServer : boolean;
    instanceID : string;
}

interface CreateController<TArgs extends any[], TMessage extends {}> {
    (
      publisher : Func<TArgs, TMessage>,
      subscriber : Action<[TMessage, TMessage | {}, string]>
    ) : Controller;
}

type Func<TArgs extends any[], TResult> = (...args : TArgs) => TResult;

interface Localsync<TArgs extends any[], TMessage> {
    (config : Config) : CreateController<TArgs, TMessage>;
}

interface LocalsyncDeprecated<TArgs extends any[], TMessage> {
    (
        channel : string,
        publisher : Func<TArgs, TMessage>,
        subscriber : Action<[TMessage]>
    ) : Controller;
}

// ----------------------------------------------------------------

const createContext = (config : Config) : Context => {
    const options = createOptions(config);
    const logger = createLogger(options);
    const isServer = detectServer();
    const isFallback = detectFallback();
    const mechanism = isServer ? "serversync" : isFallback ? "cookiesync" : "storagesync";
    return { options, logger, mechanism, isServer, isFallback };
};

const createFallbackOptions = (fallback : Partial<FallbackOptions> = {}) : FallbackOptions => {
    return {
        pollFrequency: 3000,
        path: "/",
        secure: false,
        httpOnly: false,
        ...fallback
    };
};

const createLogger = (options : Options) : Logger => {
    const supportsLevel = supportsLevelFactory(options);
    const supportsDebug = supportsLevel(LogLevel.DEBUG);
    const supportsInfo = supportsLevel(LogLevel.INFO);
    const supportsWarn = supportsLevel(LogLevel.WARN);
    const supportsError = supportsLevel(LogLevel.ERROR);
    return {
        debug(message : string) {
            if (supportsDebug) {
                console.debug(message);
            }
        },
        info(message : string) {
            if (supportsInfo) {
                console.info(message);
            }
        },
        warn(message : string) {
            if (supportsWarn) {
                console.warn(message);
            }
        },
        error(message : string) {
            if (supportsError) {
                console.error(message);
            }
        }
    };
};

const createOptions = (config : Config) : Options => {
    const isChannelOk = typeof config.channel === "string" && config.channel.length > 0;

    if (!isChannelOk) {
        throw new Error("required a channel config (string).\n\tThe channel is used to identity unique channels for pub/sub messages.");
    }

    const level = config.level ? config.level : process.env.NODE_ENV === "development" ? LogLevel.INFO : LogLevel.ERROR;

    return {
        ...config,
        level,
        fallback: createFallbackOptions(config.fallback)
    };
};

const detectFallback = () => {
    if (!navigator) {
        return false;
    }

    const isEdgeOrIE = navigator.appName === "Microsoft Internet Explorer" || (navigator.appName === "Netscape" && /(Trident|Edge)/i.test(navigator.appVersion));

    return isEdgeOrIE;
};

const detectServer = () => typeof navigator === "undefined";

const supportsLevelFactory = (options: Options) => {
    switch (options.level) {
        case LogLevel.DEBUG:
            return (level: LogLevel) =>
              level === LogLevel.DEBUG ||
              level === LogLevel.INFO ||
              level === LogLevel.WARN ||
              level === LogLevel.ERROR;
        case LogLevel.INFO:
            return (level: LogLevel) =>
              level === LogLevel.INFO ||
              level === LogLevel.WARN ||
              level === LogLevel.ERROR;
        case LogLevel.WARN:
            return (level: LogLevel) =>
              level === LogLevel.WARN || level === LogLevel.ERROR;
        case LogLevel.ERROR:
            return (level: LogLevel) => level === LogLevel.ERROR;
    }
};

// --------------------------------------------------------------

export const createCookieSync = () => {
    const mechanism = "cookiesync";

    const ID_LENGTH = 8;

    interface CookieValue<TMessage> {
        instanceID : string;
        payload : TMessage;
        url : string;
    }

    export const cookiesync = (context: Context) => {
      const createCookieController = <TArgs extends any[], TMessage extends {}>(
        publisher: Func<TArgs, TMessage>,
        subscriber: Action<[TMessage, TMessage | {}, string]>
      ): Controller => {
        const cookieOpts = {
          path: context.options.fallback.path,
          secure: context.options.fallback.secure,
          httpOnly: context.options.fallback.httpOnly
        };
        const cookieKey = `cookiesync_fallback_${context.options.channel}`;
        const instanceID = (N =>
          (Math.random().toString(36) + "00000000000000000").slice(2, N + 2))(
          ID_LENGTH
        );
        const loadCookie = (): CookieValue<TMessage | {}> => {
          try {
            const stringValue = cookie.get(cookieKey);
            if (stringValue !== undefined && stringValue !== null) {
              const value = JSON.parse(stringValue) as CookieValue<TMessage>;
              const { instanceID, payload } = value;
              if (!instanceID) {
                throw new Error(
                  `cookiesync cookies must have an instanceID associated => ${JSON.stringify(
                    value
                  )}`
                );
              }
              if (
                typeof instanceID !== "string" ||
                instanceID.length !== ID_LENGTH
              ) {
                throw new Error("instanceID must be a string of length 8");
              }
              if (!payload) {
                throw new Error(
                  `cookiesync cookies must have a payload associated => ${JSON.stringify(
                    value
                  )}`
                );
              }
              context.logger.debug(`loadCookie: ${stringValue}`);
              return value;
            }
          } catch (error) {
            context.logger.error(
              `${error.message} | loadCookie => error occurred in cookiesync, wiping cookie with key ${cookieKey}`
            );
            cookie.erase(cookieKey);
          }
          return { instanceID, payload: {}, url: window.location.href };
        };
        const saveCookie = (...args: [TMessage | {}]) => {
          if (args.length !== 1) {
            throw new Error("should only have one argument");
          }
          const [payload] = args;
          const value: CookieValue<TMessage | {}> = {
            instanceID,
            payload,
            url: window.location.href
          };
          context.logger.debug(`saveCookie | ${instanceID} | ${payload}`);
          cookie.set(cookieKey, JSON.stringify(value), cookieOpts);
        };

        let isRunning = false;
        const trigger = (...args: TArgs) => {
          context.logger.debug(`trigger | ${instanceID} (${args.join(", ")})`);
          const message = publisher(...args);
          context.logger.debug(`trigger => ${message}`);
          saveCookie(message);
        };

        let intervalID: NodeJS.Timeout;
        const start = (sync = false) => {
          context.logger.debug(`start: ${instanceID}`);
          let last = loadCookie();
          if (!last) {
            context.logger.debug(`start: nolast | ${instanceID}`);
            last = { instanceID, payload: {}, url: window.location.href };
            saveCookie(last);
          }
          intervalID = setInterval(() => {
            context.logger.debug(`poll | ${instanceID}`);
            let current = loadCookie();
            if (!current) {
              context.logger.debug(`poll: nocurrent | ${instanceID}`);
              current = last;
              saveCookie(current);
            }
            /** DONT NOTIFY IF SAME TAB */
            if (current.instanceID === instanceID) {
              context.logger.debug(`poll: sameinstance | ${instanceID}`);
              return;
            }

            if (JSON.stringify(last.payload) != JSON.stringify(current.payload)) {
              context.logger.debug(`poll: INVOKE|instanceID =${instanceID}`);
              subscriber(
                current.payload as TMessage,
                last ? last.payload : {},
                last ? last.url || "" : ""
              );
              last = current;
            } else {
              context.logger.debug(`poll: NOINVOKE|instanceID =${instanceID}`);
            }
          }, context.options.fallback.pollFrequency);
          if (sync) {
            let current = loadCookie();
            subscriber(
              current.payload as TMessage,
              last ? last.payload : {},
              last ? last.url || "" : ""
            );
            last = current;
          }
          isRunning = true;
        };

        const stop = () => {
          context.logger.debug(`stop | ${instanceID}`);
          clearInterval(intervalID);
          isRunning = false;
        };

        return {
          start,
          stop,
          trigger,
          get isRunning() {
            return isRunning;
          },
          mechanism,
          isFallback: true,
          isServer: false,
          instanceID
        };
      };
      return createCookieController;
    };
};


const createLocalSync = () => {
    const getSynchronizer = (context: Context) => {
      switch (context.mechanism) {
        case "serversync":
          return serversync(context);
        case "cookiesync":
          return cookiesync(context);
        case "storagesync":
          return storagesync(context);
        default:
          throw new Error(`Unknown mechanism: ${context.mechanism}`);
      }
    };

    export const localsync = (config: Config) => {
      const context = createContext(config);
      const synchronizer = getSynchronizer(context);
      const createSynchronizer = <TArgs extends any[], TMessage>(
        publisher: Func<TArgs, TMessage>,
        subscriber: Func<[TMessage, TMessage | {}, string], void>
      ): Controller => {
        if (!publisher) {
          throw new Error(
            "localsync requires a publisher parameter (Func<TArgs, TMessage>).\n\tThe publisher runs when trigger is invoked and used to select data to be transmitted to other tabs."
          );
        }
        if (!subscriber) {
          throw new Error(
            "localsync requires a subscriber parameter (Func<[TMessage], void>).\n\tThe subscriber is called when a trigger occurs on another tab and is used to receive published messages from other tabs."
          );
        }

        return synchronizer(publisher, subscriber);
      };
      return createSynchronizer;
    };
};

const createServerSync = (context: Context) => {
  const createServerController = <TArgs extends any[], TMessage extends {}>(
    publisher: Func<TArgs, TMessage>,
    _subscriber: Action<[TMessage, TMessage | {}, string]>
  ): Controller => {
    let isRunning = false;

    const trigger = (...args: TArgs) => {
      context.logger.debug(`trigger(${args.join(",")}`);
      const value = publisher(...args);
      context.logger.debug(`trigger TMessage: ${value}`);
    };

    const start = () => {
      context.logger.debug("serversync#start");
      isRunning = true;
    };

    const stop = () => {
      context.logger.debug("serversync#stop");
      isRunning = false;
    };

    return {
      start,
      stop,
      trigger,
      get isRunning() {
        return isRunning;
      },
      mechanism,
      isFallback: false,
      isServer: true,
      instanceID: "server"
    };
  };
  return createServerController;
};

const createStorageSync = (context: Context) => {
  const createStorageController = <TArgs extends any[], TMessage extends {}>(
    publisher: Func<TArgs, TMessage>,
    subscriber: Action<[TMessage, TMessage | {}, string]>
  ): Controller => {
    let isRunning = false;
    let last: TMessage | {} = {};

    const trigger = (...args: TArgs) => {
      context.logger.debug(`trigger(${args.join(", ")})`);
      const value = publisher(...args);
      ls(context.options.channel, value);
    };

    const notifySubscriber = (value: TMessage) => {
      subscriber(value, last, "");
      last = value;
    };
    const start = (sync = false) => {
      context.logger.debug(`start(sync = ${sync})`);
      ls.on(context.options.channel, notifySubscriber);
      if (sync) {
        const value = ls.get(context.options.channel);
        notifySubscriber(value);
      }
      isRunning = true;
    };

    const stop = () => {
      context.logger.debug("stop()");
      ls.off(context.options.channel, notifySubscriber);
      isRunning = false;
    };

    return {
      start,
      stop,
      trigger,
      get isRunning() {
        return isRunning;
      },
      mechanism,
      isFallback: false,
      isServer: false,
      instanceID: "storage"
    };
  };
  return createStorageController;
};
