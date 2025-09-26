import sys
import mimetypes

import requests

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *



def parseData ():
    nextPersonId = 1

    allGenres = {}
    allCountries = {}
    allPeople = {}
    allMovies = {}

    for data in readJson('./items.json'):
        movies = data['data']['movieListBySlug']['movies']['items']

        for movie in movies:
            position = movie['position']
            rate     = movie['rate']
            votes    = movie['votes']

            movie = movie['movie']

            url = movie['url']

            title     = movie['title']['original']
            titleRu   = movie['title']['russian']
            top250Pos = movie['ratingLists']['top250']['position']

            kpRating = movie['rating']['kinopoisk']['value']
            kpVotes  = movie['rating']['kinopoisk']['count']
            prodYear = movie['productionYear']
            movieId  = movie['id']
            genres   = []

            for genre in movie['genres']:
                allGenres[genre['id']] = genre['name']
                genres.append(genre['id'])

            posterUrl = movie['gallery']['posters']['vertical']['avatarsUrl']
            assert posterUrl.startswith('//')
            posterUrl = f'https:{ posterUrl }'

            premiereDate = (((movie.get('distribution', {}) or {}).get('worldPremiere', {}) or {}).get('incompleteDate', {}) or {}).get('date', None)

            directors = []
            countries = []
            actors = []

            for source, target in [
                [ movie['directors']['items'], directors ],
                [ movie['cast']['items'], actors ],
            ]:
                for director in source:
                    director = director['person']
                    name     = director['originalName']
                    nameRu   = director['name']

                    if nameRu is None:
                        nameRu = name
                        name   = None

                    isFound = False

                    name1 = (nameRu or '').lower() or None
                    name2 = (name or '').lower() or None

                    # ru, o
                    for dirId, names in allPeople.items():
                        norm, comp = names

                        if (name1 is not None and name1 in comp) or (name2 is not None and name2 in comp):
                            norm[0] = norm[0] or nameRu
                            norm[1] = norm[1] or name

                            comp[0] = comp[0] or name1
                            comp[1] = comp[1] or name1

                            target.append(dirId)

                            isFound = True

                            break

                    if not isFound:
                        allPeople[nextPersonId] = [
                            [ nameRu, name ],
                            [ name1, name2 ],
                        ]

                        target.append(nextPersonId)

                        nextPersonId += 1

            for country in movie['countries']:
                allCountries[country['id']] = country['name']
                countries.append(country['id'])

            allMovies[movieId] = {
                'id': movieId,
                'posterUrl': posterUrl,
                'title': {
                    'russian': titleRu,
                    'original': title
                },
                'rating': {
                    'top250rank': top250Pos,
                    'rating': kpRating,
                    'votes': kpVotes,                    
                },
                'dates': {
                    'productionYear': prodYear,
                    'premiereDate': premiereDate   
                },
                'genres': genres,
                'directors': directors,
                'countries': countries,
                'actors': actors,      
            }

            # pjp(movie['cast'])
            # print(directors, actors)
            # pjp(directors)

    tmp = list(allCountries.items())
    tmp.sort(key=lambda c: c[1])

    tmp2 = {}
    tmp3 = 1
    tmp4 = {}

    for oId, name in tmp:
        tmp2[oId] = tmp3
        tmp4[tmp3] = name

        tmp3 += 1

    allCountries = tmp4

    for m in allMovies.values():
        for i, oId in enumerate(m['countries']):
            m['countries'][i] = tmp2[oId]

    tmp = list(allGenres.items())
    tmp.sort(key=lambda c: c[1])

    tmp2 = {}
    tmp3 = 1
    tmp4 = {}

    for oId, name in tmp:
        tmp2[oId] = tmp3
        tmp4[tmp3] = name

        tmp3 += 1

    allGenres = tmp4

    for m in allMovies.values():
        for i, oId in enumerate(m['genres']):
            m['genres'][i] = tmp2[oId]

    for personId, names in allPeople.items():
        allPeople[personId] = {
            'russian': names[0][0],
            'original': names[0][1],
        }

    # ------

    allGenres = [ {
        'id': g[0],
        'name': g[1]
    } for g in allGenres.items() ]

    allCountries = [ {
        'id': c[0],
        'name': c[1]
    } for c in allCountries.items() ]

    allPeople = [ {
        'id': p[0],
        'russian': p[1]['russian'],
        'original': p[1]['original'],
    } for p in allPeople.items() ]

    allMovies = list(allMovies.values())

    nextMovieId = 1

    for m in allMovies:
        m['kpId'] = m['id']
        m['id']   = nextMovieId

        nextMovieId += 1

    return {
        'genres': allGenres,
        'countries': allCountries,
        'people': allPeople,
        'movies': allMovies,
    }


# https://www.npmjs.com/package/better-sqlite3
def main ():
    # db = parseData()

    # pjp(db)

    # return 

    data = readJson(r'C:\Projects\JSProjects\JobTestTasks\EffectiveMobile\server\data\movies.json')

    for platform in data['platforms']:
        platformId = platform['id']
        logoUrl    = platform['logoUrl']

        print(platformId, logoUrl)

        response = requests.get(logoUrl, headers={
            "Accept": "image/webp, image/apng, image/*, */*"
        })

        # # Check if the request was successful
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

        mimeType = response.headers.get('Content-Type')

        ext = mimetypes.guess_extension(mimeType) or '.bin'

        writeBin(f'./platforms/{ platformId }{ ext }', response.content)


    


r'''
position 21 (in top-250)
rate 7.893
votes 147814
movie:
    url https://www.kinopoisk.ru/film/42782/
    title:
        russian
        original
    ratingLists
        top250
            position
    rating
        kinopoisk
            count (votes)
            value (rating in top-250)
    productionYear 1965
    duration: 95
    id 42782
    genres: [
        {
            name,
            id
        }
    ]
    gallery: ???
        posters
            vertical
                avatarsUrl
    distribution ???
    directors ???
    countries: [
        {
            name,
            id
        }
    ]
    cast ???
'''






if __name__ == '__main__':
    main()
