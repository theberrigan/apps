const fs = require('fs');


const USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 YaBrowser/25.8.0.0 Safari/537.36';
const TOP250_FILE_PATH = './top250.json';



const toJson = data => JSON.stringify(data, null, 4);

const fetchData = async (url, options) => {
    const [ response, error ] = await fetch(url, options).then((response) => {
        return [ response, null ];
    }).catch((error) => {
        return [ null, error ];
    });

    if (error) {
        return [ response, error ];            
    }

    if (response.status < 200 || response.status >= 400) {
        return [ response, new Error(`Response status code: ${ response.status }`) ];
    }

    return [ response, null ];
};


const fetchMoviesPage = async (offset, limit) => {
    const query = {
        operationName: 'MovieDesktopListPage',
        variables: {
            slug: 'top250',
            platform: 'DESKTOP',
            withUserData: true,
            supportedFilterTypes: [
                'BOOLEAN',
                'SINGLE_SELECT'
            ],
            filters: {
                booleanFilterValues: [],
                intRangeFilterValues: [],
                singleSelectFilterValues: [],
                multiSelectFilterValues: [],
                realRangeFilterValues: []
            },
            singleSelectFiltersLimit: 700,
            singleSelectFiltersOffset: 0,
            moviesLimit: limit,
            moviesOffset: offset,
            moviesOrder: 'POSITION_ASC',
            supportedItemTypes: [
                'COMING_SOON_MOVIE_LIST_ITEM',
                'MOVIE_LIST_ITEM',
                'TOP_MOVIE_LIST_ITEM',
                'POPULAR_MOVIE_LIST_ITEM',
                'MOST_PROFITABLE_MOVIE_LIST_ITEM',
                'MOST_EXPENSIVE_MOVIE_LIST_ITEM',
                'BOX_OFFICE_MOVIE_LIST_ITEM',
                'OFFLINE_AUDIENCE_MOVIE_LIST_ITEM',
                'RECOMMENDATION_MOVIE_LIST_ITEM',
                'MOVIE_IN_CINEMA_LIST_ITEM',
                'PLANNED_TO_WATCH_LIST_ITEM'
            ]
        },
        query: 'query MovieDesktopListPage($slug: String!, $platform: WebClientPlatform!, $withUserData: Boolean!, $supportedFilterTypes: [FilterType]!, $filters: FilterValuesInput, $singleSelectFiltersLimit: Int!, $singleSelectFiltersOffset: Int!, $moviesLimit: Int, $moviesOffset: Int, $moviesOrder: MovieListItemOrderBy, $supportedItemTypes: [MovieListItemType]) { movieListBySlug(slug: $slug, supportedFilterTypes: $supportedFilterTypes, filters: $filters) { ...MovieListCompositeName ...MovieListAvailableFilters ...MovieList ...DescriptionLink __typename } webPage(platform: $platform) { kpMovieListPage(movieListSlug: $slug) { htmlMeta { ...OgImage __typename } __typename } __typename } } fragment ToggleFilter on BooleanFilter { id enabled name { russian __typename } __typename } fragment SingleSelectFilters on SingleSelectFilter { id name { russian __typename } hint { russian __typename } values(offset: $singleSelectFiltersOffset, limit: $singleSelectFiltersLimit) { items { name { russian __typename } selectable value __typename } __typename } __typename } fragment MoviePosterGallery on Movie { gallery { posters { vertical { avatarsUrl __typename } __typename } logos { rightholderForPoster { avatarsUrl __typename } __typename } __typename } __typename } fragment RatingValue on RatingValue { value isActive count __typename } fragment TicketOptionPurchasable on Movie { ticketOption { purchasable __typename } __typename } fragment MovieIsTicketsAvailable on Movie { ...TicketOptionPurchasable __typename } fragment MovieListReleases on Distribution { rusRelease: releases(types: [CINEMA], rerelease: false, countryId: 2, limit: 1) { items { date { date accuracy __typename } __typename } __typename } worldPremiere { incompleteDate { date accuracy __typename } __typename } allReleases: releases(limit: 1) { items { date { date accuracy __typename } __typename } __typename } __typename } fragment MovieRatingListsItem on MovieInList { movieListSlug position __typename } fragment Folder on Folder { id name public __typename } fragment MovieUserFolders on Movie { userData { userFolders(offset: 0, limit: 20) { items { ...Folder __typename } __typename } isFavorite __typename } __typename } fragment MovieListUserData on Movie { userData { watchStatuses { notInterested { value __typename } watched { value __typename } __typename } voting { value votedAt __typename } isPlannedToWatch __typename } ...MovieUserFolders __typename } fragment MovieListCompositeName on MovieListMeta { compositeName { parts { ... on FilterReferencedMovieListNamePart { filterValue { ... on SingleSelectFilterValue { filterId __typename } __typename } name __typename } ... on StaticMovieListNamePart { name __typename } __typename } __typename } __typename } fragment MovieListAvailableFilters on MovieListMeta { availableFilters { items { ... on BooleanFilter { ...ToggleFilter __typename } ... on SingleSelectFilter { ...SingleSelectFilters __typename } __typename } __typename } __typename } fragment MovieList on MovieListMeta { id name description cover { avatarsUrl __typename } movies(limit: $moviesLimit, offset: $moviesOffset, orderBy: $moviesOrder, supportedItemTypes: $supportedItemTypes) { total items { movie { id contentId title { russian original __typename } ...MoviePosterGallery countries { id name __typename } genres { id name __typename } cast: members(role: [ACTOR], limit: 3) { items { details person { name originalName __typename } __typename } __typename } directors: members(role: [DIRECTOR], limit: 1) { items { details person { name originalName __typename } __typename } __typename } url rating { kinopoisk { ...RatingValue __typename } plannedToWatch { ...RatingValue __typename } __typename } mainTrailer { id isEmbedded __typename } viewOption { buttonText originalButtonText promotionIcons { avatarsUrl fallbackUrl __typename } isAvailableOnline: isWatchable(filter: {anyDevice: false, anyRegion: false}) purchasabilityStatus type rightholderLogoUrlForPoster availabilityAnnounce { availabilityDate type groupPeriodType announcePromise __typename } __typename } ...MovieIsTicketsAvailable distribution { ...MovieListReleases __typename } ... on Film { productionYear duration isShortFilm ratingLists { top250 { ...MovieRatingListsItem __typename } __typename } __typename } ... on TvSeries { releaseYears { start end __typename } totalDuration ratingLists { top250 { ...MovieRatingListsItem __typename } __typename } __typename } ... on MiniSeries { releaseYears { start end __typename } totalDuration ratingLists { top250 { ...MovieRatingListsItem __typename } __typename } __typename } ... on TvShow { releaseYears { start end __typename } totalDuration ratingLists { top250 { ...MovieRatingListsItem __typename } __typename } __typename } ... on Video { productionYear duration isShortFilm __typename } ...MovieListUserData @include(if: $withUserData) __typename } ... on TopMovieListItem { position positionDiff rate votes __typename } ... on MostProfitableMovieListItem { boxOffice { amount __typename } budget { amount __typename } ratio __typename } ... on MostExpensiveMovieListItem { budget { amount __typename } __typename } ... on OfflineAudienceMovieListItem { viewers __typename } ... on PopularMovieListItem { positionDiff __typename } ... on BoxOfficeMovieListItem { boxOffice { amount __typename } __typename } ... on RecommendationMovieListItem { __typename } ... on ComingSoonMovieListItem { releaseDate { date accuracy __typename } __typename } ... on MoviesInCinemaListItem { promo __typename } ... on PlannedToWatchMovieListItem { votes __typename } __typename } __typename } __typename } fragment DescriptionLink on MovieListMeta { descriptionLink { title url __typename } __typename } fragment OgImage on HtmlMeta { openGraph { image { avatarsUrl __typename } __typename } __typename } '
    };

    const url = new URL('https://graphql.kinopoisk.ru/graphql/');

    url.searchParams.set('operationName', 'MovieDesktopListPage');

    const [ response, error ] = await fetchData(url, {
        method: 'POST',
        body: JSON.stringify(query),
        headers: {
            'Accept-Language': 'ru,en;q=0.9',
            'Content-Type': 'application/json',
            'Service-Id': '25',
            'User-Agent': USER_AGENT,
        },
        referrer: 'https://www.kinopoisk.ru/',
        mode: 'cors',
        credentials: 'include'
    });

    if (error) {
        throw error;       
    }

    let data = await response.json();

    data = data?.data?.movieListBySlug?.movies;

    if (!data) {
        throw new Error('Failed to fetch movies page, movies data is not found');
    }

    return [ data.items, data.total ];
};


const fetchMovies = async () => {
    const itemsPerPage = 50;

    let itemsLoaded = 0;
    let movies = [];

    while (true) {
        console.log(itemsLoaded, itemsPerPage);

        const [ pageMovies, totalCount ] = await fetchMoviesPage(itemsLoaded, itemsPerPage);

        movies = movies.concat(pageMovies);

        itemsLoaded += itemsPerPage;

        if (itemsLoaded >= totalCount) {
            break;
        }
    }

    return movies;
};


const fetchMovieData = async (movieId) => {
    const query = {
        operationName: 'FilmBaseInfo',
        variables: {
            filmId: movieId,
            isAuthorized: true,
            actorsLimit: 10,
            voiceOverActorsLimit: 5,
            relatedMoviesLimit: 14,
            clientContext: {
                clientName: 'web',
                paymentType: 'NATIVE',
                context: [
                    {
                        name: 'point_of_sale',
                        value: 'filmPage'
                    }
                ]
            },
            checkSilentInvoiceAvailability: true,
            withPurchaseOptions: true,
            watchabilityLimit: 20
        },
        query: 'query FilmBaseInfo($filmId: Long!, $isAuthorized: Boolean!, $clientContext: BillingFeatureClientContextInput!, $checkSilentInvoiceAvailability: Boolean!, $withPurchaseOptions: Boolean!, $actorsLimit: Int, $voiceOverActorsLimit: Int, $relatedMoviesLimit: Int, $watchabilityLimit: Int) { film(id: $filmId) { id contentId isTvOnly ...MovieRatingLists shortDescription synopsis title { russian original __typename } productionYear productionStatus productionStatusUpdateDate genres { id name slug __typename } ...MovieCinemaAnnounce ott { preview { ...OttPreviewAvailableMetaData ... on OttPreview_AbstractVideo { duration timing @include(if: $isAuthorized) { current maximum __typename } __typename } ...OttPreviewFeatures __typename } promoTrailers: trailers(onlyPromo: true, limit: 1) { items { streamUrl __typename } __typename } ... on Ott_AbstractVideo { skippableFragments { startTime endTime type __typename } __typename } __typename } editorAnnotation countries { id name __typename } restriction { age mpaa __typename } mainTrailer { id title preview { avatarsUrl fallbackUrl __typename } duration createdAt isEmbedded __typename } releaseOptions { isImax is3d __typename } ...MovieCover viewOption { ...ViewOption __typename } externalViewOptions { ...ExternalViewOptions __typename } actors: members(limit: $actorsLimit, role: [ACTOR, CAMEO, UNCREDITED]) { items { person { id name originalName __typename } __typename } total __typename } voiceOverActors: members(limit: $voiceOverActorsLimit, role: VOICEOVER) { items { person { id name originalName __typename } __typename } total __typename } tagline directors: members(role: DIRECTOR, limit: 4) { items { person { id name originalName __typename } __typename } __typename } writers: members(role: WRITER, limit: 4) { items { person { id name originalName __typename } __typename } __typename } producers: members(role: PRODUCER, limit: 4) { items { person { id name originalName __typename } __typename } __typename } operators: members(role: OPERATOR, limit: 4) { items { person { id name originalName __typename } __typename } __typename } composers: members(role: COMPOSER, limit: 4) { items { person { id name originalName __typename } __typename } __typename } designers: members(role: [PRODUCTION_DESIGNER, DESIGN, ART, COSTUMER, DECORATOR], limit: 13) { items { person { id name originalName __typename } __typename } __typename } filmEditors: members(role: EDITOR, limit: 4) { items { person { id name originalName __typename } __typename } __typename } boxOffice { budget { amount currency { symbol __typename } __typename } rusBox { amount currency { symbol __typename } __typename } usaBox { amount currency { symbol __typename } __typename } worldBox { amount currency { symbol __typename } __typename } marketing { amount currency { symbol __typename } __typename } __typename } ...MoviePoster rating { imdb { ...RatingValue __typename } kinopoisk { ...RatingValue __typename } russianCritics { ...RatingValue __typename } worldwideCritics { value percent count isActive positiveCount negativeCount __typename } reviewCount { ...RatingValue __typename } plannedToWatch { ...RatingValue __typename } __typename } duration keywords(limit: 0) { total __typename } awards(limit: 0) { total __typename } premieres(limit: 0) { total __typename } relatedMovies(limit: 0) { total __typename } images(limit: 0) { total __typename } ...MovieImagesStats soundtrack(limit: 0) { total __typename } production(limit: 0) { total __typename } negativeCriticReviews: criticReviews(types: NEGATIVE, limit: 0) { total __typename } positiveCriticReviews: criticReviews(types: POSITIVE, limit: 0) { total __typename } audience(limit: 3) { total items { count country { id name __typename } __typename } __typename } releases { date releasers { id name __typename } type __typename } worldPremiere { incompleteDate { accuracy date __typename } __typename } distribution { rusRelease: releases(types: [CINEMA], rerelease: false, countryId: 2, limit: 1) { ...releasesInfoFragment __typename } digitalRelease: releases(types: [DIGITAL], limit: 1) { ...releasesInfoFragment __typename } reRelease: releases(types: [CINEMA], rerelease: true, countryId: 2, limit: 1) { ...releasesInfoFragment __typename } originals: releases(original: true, types: [DIGITAL], limit: 1) { ...OriginalsFragment __typename } __typename } filmMainAward: awards(isMain: true, limit: 15) { items { nomination { award { title slug year __typename } title __typename } win __typename } total __typename } filmAwardWins: awards(isMain: true, isWin: true, limit: 0) { total __typename } ...MovieUserData @include(if: $isAuthorized) sequelsPrequels: relatedMovies(limit: $relatedMoviesLimit, type: [BEFORE, AFTER, REMAKE], orderBy: PREMIERE_DATE_ASC) { total limit offset items { relationType movie { id title { russian original __typename } countries { id name __typename } poster { avatarsUrl fallbackUrl __typename } genres { id name slug __typename } rating { kinopoisk { ...RatingValue __typename } __typename } viewOption { buttonText isAvailableOnline: isWatchable(filter: {anyDevice: false, anyRegion: false}) purchasabilityStatus contentPackageToBuy { billingFeatureName __typename } subscriptionBadge { image { avatarsUrl __typename } __typename } type posterWithRightholderLogo __typename } userData @include(if: $isAuthorized) { watchStatuses { watched { value __typename } __typename } __typename } ... on Film { productionYear __typename } ... on Video { productionYear __typename } ... on TvSeries { releaseYears { start end __typename } __typename } ... on TvShow { releaseYears { start end __typename } __typename } ... on MiniSeries { releaseYears { start end __typename } __typename } __typename } __typename } __typename } watchability(limit: $watchabilityLimit) { items { platform { name logo { avatarsUrl __typename } __typename } url __typename } __typename } ...MovieSeoInfo ...MovieFactsCount ...MovieBloopersCount ...MovieUsersReviewsCount ...MovieMediaPostsCount ...MovieTrailersCount ...MovieCriticReviewsCount ...MovieSimilarMoviesCount ...MovieOriginalMoviesCount __typename } tvSeries(id: $filmId) { id __typename } webPage(platform: DESKTOP) { kpFilmPage(filmId: $filmId) { htmlMeta { ...OgImage __typename } __typename } __typename } } fragment MovieRatingListsItem on MovieInList { movieListSlug position __typename } fragment TicketOptionPurchasable on Movie { ticketOption { purchasable __typename } __typename } fragment MovieIsTicketsAvailable on Movie { ...TicketOptionPurchasable __typename } fragment TicketOptionReleaseAnnounce on Movie { ticketOption { releaseAnnounce { available releaseDate { accuracy date __typename } __typename } __typename } __typename } fragment ShortImage on Image { avatarsUrl fallbackUrl __typename } fragment AvailabilityAnnounce on AvailabilityAnnounce { availabilityDate groupPeriodType type announcePromise __typename } fragment CompositeOffersPlan on OfferPlanUnion { __typename ... on TrialUntilPlan { until __typename } ... on IntroUntilPlan { until __typename } ... on TrialPlan { period __typename } ... on IntroPlan { period __typename } } fragment CompositeOffer on PlusCompositeOffer { asset { subscriptionName __typename } positionId structureType silentInvoiceAvailable forActiveOffers { ... on PlusOptionOffer { name __typename } ... on PlusTariffOffer { name __typename } __typename } optionOffers { commonPeriod text additionText name option { name __typename } plans { ...CompositeOffersPlan __typename } __typename } tariffOffer { commonPeriod text additionText name tariff { name __typename } plans { ...CompositeOffersPlan __typename } __typename } invoices { timestamp totalPrice { amount currency __typename } __typename } __typename } fragment CustomPayload on OttCompositeOfferCustomPayload { overridedText overridedAdditionalText __typename } fragment SubscriptionCompositeOffers on SubscriptionCompositeOffers { batchPositionId eventSessionId offers { compositeOffer { ...CompositeOffer __typename } customPayload { ...CustomPayload __typename } __typename } __typename } fragment SubscriptionPurchaseOptions on BillingFeaturePurchaseOptions { target billingFeatureNames interfaceMeta subscriptionCompositeOffers(checkSilentInvoiceAvailability: $checkSilentInvoiceAvailability) { ...SubscriptionCompositeOffers __typename } __typename } fragment ContentBrand on ContentBrand { id name gallery { logos { square { avatarsUrl __typename } __typename } __typename } colors { main __typename } userData @include(if: $isAuthorized) { isLiked __typename } __typename } fragment ExternalViewOptionAction on ExternalPartnerOption { action { ... on BillingFeaturePurchaseAction { purchaseOptionCustomProperties __typename } __typename } __typename } fragment MovieMarketingVerticalPoster on Movie { gallery { posters { marketingVertical: vertical(override: MARKETING_WHEN_EXISTS) { ...ShortImage __typename } __typename } __typename } __typename } fragment MovieKpVerticalPoster on Movie { gallery { posters { kpVertical: vertical { ...ShortImage __typename } __typename } __typename } __typename } fragment PurchaseMetadata on MovieUserData { purchaseMetadata(includeWaiting: true) { id watchPeriod { watchPeriodStatus __typename } __typename } __typename } fragment Folder on Folder { id name public __typename } fragment MovieUserFolders on Movie { userData { userFolders(offset: 0, limit: 20) { items { ...Folder __typename } __typename } isFavorite __typename } __typename } fragment VideoInterface on VideoInterface { duration kpProductionYear: productionYear(override: DISABLED) ottProductionYear: productionYear(override: OTT_WHEN_EXISTS) __typename } fragment OriginalsFragment on PagingList_Release { items { companies { displayName id originalsMovieList { id url movies(supportedItemTypes: [MOVIE_LIST_ITEM], limit: 0) { total __typename } __typename } __typename } __typename } __typename } fragment MovieRatingLists on Movie { ratingLists { top10 { ...MovieRatingListsItem __typename } top250 { ...MovieRatingListsItem __typename } __typename } __typename } fragment MovieCinemaAnnounce on Movie { ...MovieIsTicketsAvailable ...TicketOptionReleaseAnnounce __typename } fragment OttPreviewAvailableMetaData on OttPreview { availableMetadata(filter: {isSupportedByClient: false}) { audio audioMeta { languageName qualityName studio type forAdult __typename } subtitles subtitleMeta { languageName type studio forAdult __typename } __typename } __typename } fragment OttPreviewFeatures on OttPreview { features(filter: {layout: OTT_TITLE_CARD, onlyClientSupported: true}) { alias group __typename } __typename } fragment MovieCover on Movie { gallery { covers { square { ...ShortImage __typename } horizontal { ...ShortImage __typename } __typename } __typename } __typename } fragment ViewOption on ViewOption { type purchasabilityStatus buttonText originalButtonText descriptionText promotionActionType texts { disclaimer __typename } rightholderLogoUrlForPoster posterWithRightholderLogo isAvailableOnline: isWatchable(filter: {anyDevice: false, anyRegion: false}) isWatchable(filter: {anyDevice: true, anyRegion: false}) watchabilityStatus promotionIcons { avatarsUrl fallbackUrl __typename } contentPackageToBuy { billingFeatureName __typename } mainPromotionAbsoluteAmount { amount __typename } mastercardPromotionAbsoluteAmount { amount __typename } optionMonetizationModels priceWithTotalDiscount { amount currency { displayName __typename } __typename } transactionalMinimumPrice { amount __typename } transactionalPrice { amount __typename } availabilityAnnounce { ...AvailabilityAnnounce __typename } purchaseOptionCustomProperties purchaseOptions(clientContext: $clientContext) @include(if: $withPurchaseOptions) { ...SubscriptionPurchaseOptions __typename } __typename } fragment ExternalViewOptions on ExternalViewOption { ... on ExternalPartnerOption { contentBrand { ...ContentBrand __typename } ...ExternalViewOptionAction externalUrl __typename } __typename } fragment MoviePoster on Movie { ...MovieMarketingVerticalPoster ...MovieKpVerticalPoster __typename } fragment RatingValue on RatingValue { value isActive count __typename } fragment MovieImagesStats on Movie { concepts: images(types: [CONCEPT], limit: 0) { total __typename } covers: images(types: [COVER], limit: 0) { total __typename } fanarts: images(types: [FAN_ART], limit: 0) { total __typename } posters: images(types: [POSTER], limit: 0) { total __typename } promos: images(types: [PROMO], limit: 0) { total __typename } screenshots: images(types: [SCREENSHOT], limit: 0) { total __typename } shootings: images(types: [SHOOTING], limit: 0) { total __typename } stills: images(types: [STILL], limit: 0) { total __typename } wallpapers: images(types: [WALLPAPER], limit: 0) { total __typename } __typename } fragment releasesInfoFragment on PagingList_Release { items { date { accuracy date __typename } companies { id slugId slug displayName __typename } __typename } __typename } fragment MovieUserData on Movie { userData { voting { value votedAt __typename } note { value makeDate __typename } watchStatuses { notInterested { value __typename } watched { value __typename } __typename } isPlannedToWatch ...PurchaseMetadata __typename } ...MovieUserFolders __typename } fragment MovieSeoInfo on Movie { id title { localized original __typename } shortDescription synopsis genres { id name slug __typename } countries { id name __typename } viewOption { isAvailableOnline: isWatchable(filter: {anyDevice: false, anyRegion: false}) availabilityAnnounce { __typename } __typename } watchabilityCount: watchability(limit: 0) { total __typename } ott { preview { features(filter: {layout: OTT_TITLE_CARD, onlyClientSupported: true}) { alias __typename } __typename } __typename } ... on Film { ...VideoInterface __typename } ... on Video { ...VideoInterface __typename } ... on Series { releaseYears { start end __typename } seasonsAll: seasons(limit: 0) { total __typename } seasonsOnline: seasons(limit: 0, isOnlyOnline: true) { total __typename } __typename } __typename } fragment MovieFactsCount on Movie { factsCount: trivias(type: FACT, limit: 0) { total __typename } __typename } fragment MovieBloopersCount on Movie { bloopersCount: trivias(type: BLOOPER, limit: 0) { total __typename } __typename } fragment MovieUsersReviewsCount on Movie { usersReviewsCount: userReviews(limit: 0) { total __typename } __typename } fragment MovieMediaPostsCount on Movie { mediaPostsCount: post(limit: 0) { total __typename } __typename } fragment MovieTrailersCount on Movie { trailersCount: trailers(limit: 0) { total __typename } __typename } fragment MovieCriticReviewsCount on Movie { criticReviewsCount: criticReviews(limit: 0) { total __typename } __typename } fragment MovieSimilarMoviesCount on Movie { similarMoviesCount: userRecommendations(limit: 0) { total __typename } __typename } fragment MovieOriginalMoviesCount on Movie { distribution { releases(original: true, types: [DIGITAL], limit: 1) { ...OriginalsFragment __typename } __typename } __typename } fragment OgImage on HtmlMeta { openGraph { image { avatarsUrl __typename } __typename } __typename } '
    };

    const url = new URL('https://graphql.kinopoisk.ru/graphql/');

    url.searchParams.set('operationName', 'FilmBaseInfo');

    const [ response, error ] = await fetchData(url, {
        method: 'POST',
        body: JSON.stringify(query),
        headers: {
            'Accept-Language': 'ru,en;q=0.9',
            'Content-Type': 'application/json',
            'Service-Id': '25',
            'User-Agent': USER_AGENT,
            'Cookie': ''
        },
        referrer: 'https://www.kinopoisk.ru/',
        mode: 'cors',
        credentials: 'include'
    });

    if (error) {
        throw error;       
    }

    let data = await response.json();

    data = data?.data?.film;

    if (!data) {
        throw new Error('Failed to fetch movie data, data is not found');
    }

    return data;
};


const getMovies = async () => {
    if (fs.existsSync(TOP250_FILE_PATH)) {
        return JSON.parse(fs.readFileSync(TOP250_FILE_PATH, 'utf8'));
    };

    const movies = await fetchMovies();

    fs.writeFileSync(TOP250_FILE_PATH, JSON.stringify(movies));

    return movies;
};

const sleep = async (delay) => {
    return new Promise((resolve) => setTimeout(resolve, delay));
};

const collectAllData = async () => {
    const movies = await getMovies();

    for (let i = 0; i < movies.length; ++i) {
        console.log(i); 

        const brief = movies[i].movie;

        if (!brief) {
            if (!movies[i].brief) {
                throw new Error('No movie data');                
            } else {
                continue;
            }
        }

        const data = await fetchMovieData(brief.id);

        movies[i] = { brief, data };

        if (i % 25 === 0) {
            fs.writeFileSync(TOP250_FILE_PATH, JSON.stringify(movies));
        }

        await sleep(2000);
    }

    fs.writeFileSync(TOP250_FILE_PATH, JSON.stringify(movies));
};

const collectAwards = (movies) => {
    const slugToTitle = {};
    const remap = {};

    movies.forEach(({ data }) => {
        data.filmMainAward.items.forEach(({ nomination, win }) => {
            const { title, slug, year } = nomination.award;

            slugToTitle[slug] = title;
        });
    });

    const table = Object.entries(slugToTitle)
        .sort((a, b) => {
            return a[1].localeCompare(b[1]);
        })
        .map(([ key, name ], i) => {
            remap[key] = i;
            
            return {
                id: i + 1,
                title: name
            };
        });

    return [ table, remap ];
};

const collectNominations = (movies) => {
    const keyToTitle = {};
    const remap = {};

    movies.forEach(({ data }) => {
        data.filmMainAward.items.forEach(({ nomination }) => {
            const { title } = nomination;

            keyToTitle[title.toLowerCase()] = title;
        });
    });

    const table = Object.entries(keyToTitle)
        .sort((a, b) => {
            return a[1].localeCompare(b[1]);
        })
        .map(([ key, name ], i) => {
            remap[key] = i;
            
            return {
                id: i + 1,
                title: name
            };
        });

    return [ table, remap ];
};

const collectPlatforms = (movies) => {
    const slugToLogo = {};
    const remap = {};

    movies.forEach(({ data }) => {
        data.watchability.items.forEach(({ platform }) => {
            const title = platform.name;
            const logoUrl = platform.logo.avatarsUrl;

            slugToLogo[title] = normalizeUrl(logoUrl, '200x200');
        });
    });

    const table = Object.entries(slugToLogo)
        .sort((a, b) => {
            return a[0].localeCompare(b[0]);
        })
        .map(([ title, logoUrl ], i) => {
            remap[title.toLowerCase()] = i;
            
            return {
                id: i + 1,
                title,
                logoUrl
            };
        });

    return [ table, remap ];
};

const normalizePerson = ({ name, originalName }) => {
    let russianName = null;
    let foreignName = null;

    [ name, originalName ].forEach((n) => {
        if (!n) {
            return;
        }

        if (n.match(/[а-яё]/i)) {
            if (russianName !== null) {
                console.log('russianName', name, originalName);
                process.exit();
            }

            russianName = n || null;
        } else {
            if (foreignName !== null) {
                console.log('foreignName', name, originalName);
                process.exit();
            }

            foreignName = n || null;
        }
    });

    console.assert(!russianName || russianName.match(/[а-яё]/i), [ 2, russianName ]);
    console.assert(!foreignName || !foreignName.match(/[а-яё]/i), [ 3, foreignName ]);

    return {
        russianName,
        foreignName,
    };
};

const getPersonKey = ({ name, originalName }) => {
    return (name || originalName).toLowerCase();
};

const collectPeople = (movies) => {
    const nameToPerson = {};
    const remap = {};

    movies.forEach(({ data }) => {
        [
            data.actors.items,
            data.voiceOverActors.items,
            data.directors.items,
            data.writers.items,
            data.producers.items,
            data.operators.items,
            data.composers.items,
            data.designers.items,
            data.filmEditors.items,
        ].forEach((items) => {
            items.forEach(({ person }) => {
                nameToPerson[getPersonKey(person)] = normalizePerson(person);
            });
        });
    });

    const table = Object.entries(nameToPerson)
        .sort((a, b) => {
            return a[0].localeCompare(b[0]);
        })
        .map(([ personKey, person ], i) => {
            remap[personKey] = i;

            person.id = i + 1;
            
            return person;
        });

    return [ table, remap ];
};

const collectCountries = (movies) => {
    const kpIdToName = {};
    const remap = {};

    movies.forEach(({ data }) => {
        data.audience.items.forEach(({ country: { id, name } }) => {
            kpIdToName[id] = name;
        });

        data.countries.forEach(({ id, name }) => {
            kpIdToName[id] = name;
        });
    });

    const table = Object.entries(kpIdToName)
        .sort((a, b) => {
            return a[1].localeCompare(b[1]);
        })
        .map(([ kpId, title ], i) => {
            remap[kpId] = i;
            
            return {
                id: i + 1,
                title,
            };
        });

    return [ table, remap ];
};

const collectGenres = (movies) => {
    const kpIdToName = {};
    const remap = {};

    movies.forEach(({ data }) => {
        data.genres.forEach(({ id, name }) => {
            kpIdToName[id] = name;
        });
    });

    const table = Object.entries(kpIdToName)
        .sort((a, b) => {
            return a[1].localeCompare(b[1]);
        })
        .map(([ kpId, title ], i) => {
            remap[kpId] = i;
            
            return {
                id: i + 1,
                title,
            };
        });

    return [ table, remap ];
};

const collectReleasers = (movies) => {
    const kpIdToName = {};
    const remap = {};

    movies.forEach(({ data }) => {
        data.releases.forEach(({ releasers }) => {
            releasers.forEach(({ id, name }) => {
                kpIdToName[id] = name;
            });
        });
    });

    const table = Object.entries(kpIdToName)
        .sort((a, b) => {
            return a[1].localeCompare(b[1]);
        })
        .map(([ kpId, title ], i) => {
            remap[kpId] = i;
            
            return {
                id: i + 1,
                title,
            };
        });

    return [ table, remap ];
};

const parseAge = (kpAge) => {
    if (!kpAge) {
        return null;
    }

    const match = kpAge.match(/^Age(\d+)$/i);

    return Number(match[1]);
};

// 300x450, 600x900
const normalizeUrl = (url, resolution = null) => {
    if (!url) {
        return null;
    }

    if (url.startsWith('//')) {
        url = 'https:' + url;
    }

    if (resolution) {
        url = url.replace(/\/+$/, '') + '/' + resolution;
    }

    return url;
};

const normalizeWatchUrl = (url) => {
    if (!url) {
        return null;
    }

    if (url.startsWith('//')) {
        url = 'https:' + url;
    }

    url = new URL(url);

    [ ...url.searchParams.keys() ].forEach((key) => {
        if (key.startsWith('utm_')) {
            url.searchParams.delete(key);
        }
    });

    return url.toString();
};

const normalizeData = () => {
    let movies = JSON.parse(fs.readFileSync(TOP250_FILE_PATH, 'utf8'));

    const [ awardsTable,      awardsRemap      ] = collectAwards(movies);
    const [ nominationsTable, nominationsRemap ] = collectNominations(movies);
    const [ platformsTable,   platformsRemap   ] = collectPlatforms(movies);
    const [ peopleTable,      peopleRemap      ] = collectPeople(movies);
    const [ countriesTable,   countriesRemap   ] = collectCountries(movies);
    const [ genresTable,      genresRemap      ] = collectGenres(movies);
    const [ releasersTable,   releasersRemap   ] = collectReleasers(movies);

    // const castTable                   = [];
    const movieToGenresTable          = [];
    const movieToCountriesTable       = [];
    const movieToActorsTable          = [];
    const movieToVoiceOverActorsTable = [];
    const movieToDirectorsTable       = [];
    const movieToWritersTable         = [];
    const movieToProducersTable       = [];
    const movieToComposersTable       = [];
    const movieToDesignersTable       = [];
    const movieToEditorsTable         = [];
    const movieToAudienceTable        = [];
    const movieToReleasesTable        = [];
    const movieToAwardsTable          = [];
    const movieToPlatformTable        = [];
    
    const moviesTable = movies.map(({ data: source }, i) => {
        const movieId = i + 1;

        const movie = {
            id: movieId,
            kpId: source.id,
            russianTitle: source.title.russian || source.title.localized,
            foreignTitle: source.title.original,
            shortDescription: source.shortDescription,
            fullDescription: source.synopsis,
            slogan: source.tagline,
            top250Position: source.ratingLists?.top250?.position ?? null,
            productionYear: source.productionYear,
            age: parseAge(source.restriction.age),
            premiereDate: source.worldPremiere?.incompleteDate?.date || null,
            posterUrl: normalizeUrl(source.gallery.posters.kpVertical.avatarsUrl || source.gallery.posters.kpVertical.fallbackUrl || source.gallery.posters.marketingVertical.avatarsUrl || source.gallery.posters.marketingVertical.fallbackUrl, '600x900'),
            duration: source.duration,
            budgetAmount: null,
            budgetCurrency: null,
            boxOfficeAmount: null,
            boxOfficeCurrency: null,
            ratingValue: source.rating.kinopoisk.value,
            ratingVoteCount: source.rating.kinopoisk.count,
        };

        if (source.boxOffice.budget) {
            movie.budgetAmount   = source.boxOffice.budget.amount;
            movie.budgetCurrency = source.boxOffice.budget.currency.symbol;
        }

        if (source.boxOffice.worldBox) {
            movie.boxOfficeAmount   = source.boxOffice.worldBox.amount;
            movie.boxOfficeCurrency = source.boxOffice.worldBox.currency.symbol;        
        }

        source.genres.forEach((genre) => {
            const genreId = genresTable[genresRemap[genre.id]].id;
            
            movieToGenresTable.push({ movieId, genreId });
        });

        source.countries.forEach((country) => {
            const countryId = countriesTable[countriesRemap[country.id]].id;
            
            movieToCountriesTable.push({ movieId, countryId });
        });

        [
            [ source.actors.items,          movieToActorsTable          ],
            [ source.voiceOverActors.items, movieToVoiceOverActorsTable ],
            [ source.directors.items,       movieToDirectorsTable       ],
            [ source.writers.items,         movieToWritersTable         ],
            [ source.producers.items,       movieToProducersTable       ],
            [ source.composers.items,       movieToComposersTable       ],
            [ source.designers.items,       movieToDesignersTable       ],
            [ source.filmEditors.items,     movieToEditorsTable         ],
        ].forEach(([ items, table ]) => {
            items.forEach(({ person }) => {
                const personId = peopleTable[peopleRemap[getPersonKey(person)]].id;

                table.push({ movieId, personId });
            });
        });

        /*
        TODO: only in brief
        source.cast?.items.forEach(({ details: role, person }) => {
            const personId = peopleTable[peopleRemap[getPersonKey(person)]].id;

            console.assert(Number.isFinite(personId), person);

            castTable.push({ movieId, personId, role });
        });
        */

        source.audience.items.forEach(({ count, country }) => {
            const countryId = countriesTable[countriesRemap[country.id]].id;

            movieToAudienceTable.push({ movieId, countryId, count });
        });

        source.releases.forEach(({ date: releaseDate, type: releaseType, releasers }) => {
            releasers.forEach((releaser) => {
                const releaserId = releasersTable[releasersRemap[releaser.id]].id;

                movieToReleasesTable.push({ movieId, releaserId, releaseType, releaseDate });
            });
        });

        let tmpAwards = {};

        source.filmMainAward.items.forEach(({ nomination, win }) => {
            const { award, title: nomTitle } = nomination;
            const { slug, year } = award;

            const awardId      = awardsTable[awardsRemap[slug]].id;
            const nominationId = nominationsTable[nominationsRemap[nomTitle.toLowerCase()]].id;

            const key = '' + movieId + '_' + awardId + '_' + nominationId + '_' + year;

            if (tmpAwards.hasOwnProperty(key)) {
                tmpAwards[key].win ||= win;
            } else {
                tmpAwards[key] = { movieId, awardId, nominationId, year, win };
            }
        });

        Object.values(tmpAwards).forEach((award) => {
            movieToAwardsTable.push(award);
        });

        source.watchability.items.forEach(({ platform, url }) => {
            const platformId = platformsTable[platformsRemap[platform.name.toLowerCase()]].id;
            const watchUrl = normalizeWatchUrl(url);

            movieToPlatformTable.push({ movieId, platformId, watchUrl });
        });

        return movie;
    });

    const db = {
        awardTitles: awardsTable,
        nominationTitles: nominationsTable,
        platforms: platformsTable,
        people: peopleTable,
        countries: countriesTable,
        genres: genresTable,
        releasers: releasersTable,
        movies: moviesTable,
        audience: movieToAudienceTable,
        releases: movieToReleasesTable,
        awards: movieToAwardsTable,
        watchUrls: movieToPlatformTable,
        movieToGenres: movieToGenresTable,
        movieToCountries: movieToCountriesTable,
        movieToActors: movieToActorsTable,
        movieToVoiceOverActors: movieToVoiceOverActorsTable,
        movieToDirectors: movieToDirectorsTable,
        movieToWriters: movieToWritersTable,
        movieToProducers: movieToProducersTable,
        movieToComposers: movieToComposersTable,
        movieToDesigners: movieToDesignersTable,
        movieToEditors: movieToEditorsTable,
    };

    fs.writeFileSync('./final_data.json', JSON.stringify(db));
};

const main = async () => {
    normalizeData();
};

main();
