import {Injectable} from '@angular/core';
import {HttpService} from './http.service';
import {catchError, map, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';

export interface FaqLang {
    code : string;
    name : string;
    isDeletable : boolean;
    isBasic : boolean;
}

@Injectable({
    providedIn: 'root'
})
export class FaqService {
    readonly editorLangs : FaqLang[] = [
        {
            code: 'en',
            name: 'English',
            isDeletable: false,
            isBasic: true
        },
        {
            code: 'es',
            name: 'Spanish',
            isDeletable: true,
            isBasic: true
        },
        {
            code: 'ab',
            name: 'Abkhazian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'aa',
            name: 'Afar',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'af',
            name: 'Afrikaans',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ak',
            name: 'Akan',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'sq',
            name: 'Albanian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'als',
            name: 'Alemannic',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'am',
            name: 'Amharic',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ang',
            name: 'Angal',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ang',
            name: 'Anglo-Saxon/Old English',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ar',
            name: 'Arabic',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'an',
            name: 'Aragonese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'arc',
            name: 'Aramaic',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'hy',
            name: 'Armenian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'roa-rup',
            name: 'Aromanian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'frp',
            name: 'Arpitan/Franco-Provençal',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'as',
            name: 'Assamese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ast',
            name: 'Asturian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'av',
            name: 'Avar',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'awa',
            name: 'Awadhi',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ay',
            name: 'Aymara',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'az',
            name: 'Azerbaijani',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'bm',
            name: 'Bambara',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'map-bms',
            name: 'Banyumasan',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ba',
            name: 'Bashkir',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'eu',
            name: 'Basque',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'bar',
            name: 'Bavarian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'be',
            name: 'Belarusian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'be-x-old',
            name: 'Belarusian (Taraškievica)',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'bn',
            name: 'Bengali',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'bh',
            name: 'Bihari',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'bcl',
            name: 'Bikol',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'bpy',
            name: 'Bishnupriya Manipuri',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'bi',
            name: 'Bislama',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'bo',
            name: 'Boro',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'bs',
            name: 'Bosnian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'br',
            name: 'Breton',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'bug',
            name: 'Buginese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'bg',
            name: 'Bulgarian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'bxr',
            name: 'Buriat (Russia)',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'my',
            name: 'Burmese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'km',
            name: 'Cambodian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'zh-yue',
            name: 'Cantonese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ca',
            name: 'Catalan',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ceb',
            name: 'Cebuano',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ch',
            name: 'Chamorro',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ce',
            name: 'Chechen',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'chr',
            name: 'Cherokee',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'chy',
            name: 'Cheyenne',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ny',
            name: 'Chichewa',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'zh',
            name: 'Chinese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'cho',
            name: 'Choctaw',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'cv',
            name: 'Chuvash',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'zh-classical',
            name: 'Classical Chinese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'kw',
            name: 'Cornish',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'co',
            name: 'Corsican',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'cr',
            name: 'Cree',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'mus',
            name: 'Creek/Muskogee',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'hr',
            name: 'Croatian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'cs',
            name: 'Czech',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'da',
            name: 'Danish',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'diq',
            name: 'Dimli',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'dv',
            name: 'Divehi',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'nl',
            name: 'Dutch',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'nds-nl',
            name: 'Dutch Low Saxon',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'dz',
            name: 'Dzongkha',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'eo',
            name: 'Esperanto',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'et',
            name: 'Estonian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ee',
            name: 'Ewe',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ext',
            name: 'Extremaduran',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'fo',
            name: 'Faroese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'fj',
            name: 'Fijian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'fi',
            name: 'Finnish',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'fr',
            name: 'French',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'fur',
            name: 'Friulian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'gl',
            name: 'Galician',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'gan',
            name: 'Gan Chinese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'lg',
            name: 'Ganda',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'gbm',
            name: 'Garhwali',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ka',
            name: 'Georgian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'de',
            name: 'German',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'gil',
            name: 'Gilbertese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'got',
            name: 'Gothic',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'el',
            name: 'Greek',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'kl',
            name: 'Greenlandic',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'gn',
            name: 'Guarani',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'gu',
            name: 'Gujarati',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ht',
            name: 'Haitian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'hak',
            name: 'Hakka Chinese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ha',
            name: 'Hausa',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'haw',
            name: 'Hawaiian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'he',
            name: 'Hebrew',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'hz',
            name: 'Herero',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'hi',
            name: 'Hindi',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ho',
            name: 'Hiri Motu',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'hu',
            name: 'Hungarian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'is',
            name: 'Icelandic',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'io',
            name: 'Ido',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ig',
            name: 'Igbo',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ilo',
            name: 'Ilokano',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'id',
            name: 'Indonesian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'inh',
            name: 'Ingush',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ia',
            name: 'Interlingua',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ie',
            name: 'Interlingue',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'iu',
            name: 'Inuktitut',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ik',
            name: 'Inupiak',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ga',
            name: 'Irish',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'it',
            name: 'Italian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ja',
            name: 'Japanese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'jv',
            name: 'Javanese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'xal',
            name: 'Kalmyk',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'kn',
            name: 'Kannada',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'kr',
            name: 'Kanuri',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'pam',
            name: 'Kapampangan',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ks',
            name: 'Kashmiri',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'csb',
            name: 'Kashubian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'kk',
            name: 'Kazakh',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'khw',
            name: 'Khowar',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ki',
            name: 'Kikuyu',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ky',
            name: 'Kirghiz',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'rn',
            name: 'Kirundi',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'tlh',
            name: 'Klingon',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'kv',
            name: 'Komi',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'kg',
            name: 'Kongo',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ko',
            name: 'Korean',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'kj',
            name: 'Kuanyama',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ku',
            name: 'Kurdish (Kurmanji)',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ckb',
            name: 'Kurdish (Sorani)',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'lad',
            name: 'Ladino/Judeo-Spanish',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'lan',
            name: 'Lango',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'lo',
            name: 'Laotian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'la',
            name: 'Latin',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'lv',
            name: 'Latvian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'lzz',
            name: 'Laz',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'lij',
            name: 'Ligurian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'li',
            name: 'Limburgian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ln',
            name: 'Lingala',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'lt',
            name: 'Lithuanian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'jbo',
            name: 'Lojban',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'lmo',
            name: 'Lombard',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'nds',
            name: 'Low German/Low Saxon',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'dsb',
            name: 'Lower Sorbian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'lb',
            name: 'Luxembourgish',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'mk',
            name: 'Macedonian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'mg',
            name: 'Malagasy',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ms',
            name: 'Malay',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ml',
            name: 'Malayalam',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'mt',
            name: 'Maltese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'man',
            name: 'Mandarin',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'gv',
            name: 'Manx',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'mi',
            name: 'Maori',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'mrh',
            name: 'Mara',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'mr',
            name: 'Marathi',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'mh',
            name: 'Marshallese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'xmf',
            name: 'Megrelian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'cdo',
            name: 'Min Dong Chinese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'min',
            name: 'Minangkabau',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'zh-min-nan',
            name: 'Minnan',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'mwl',
            name: 'Mirandese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'mo',
            name: 'Moldovan',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'mn',
            name: 'Mongolian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'nah',
            name: 'Nahuatl',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'na',
            name: 'Nauruan',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'nv',
            name: 'Navajo',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ng',
            name: 'Ndonga',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'nap',
            name: 'Neapolitan',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ne',
            name: 'Nepali',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'new',
            name: 'Newar',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'pih',
            name: 'Norfolk',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'nrm',
            name: 'Norman',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'nd',
            name: 'North Ndebele',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'se',
            name: 'Northern Sami',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'nso',
            name: 'Northern Sotho',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'no',
            name: 'Norwegian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'nn',
            name: 'Norwegian Nynorsk',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'oc',
            name: 'Occitan',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'oj',
            name: 'Ojibwa',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'cu',
            name: 'Old Church Slavonic/Old Bulgarian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'or',
            name: 'Oriya',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'om',
            name: 'Oromo',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'os',
            name: 'Ossetian/Ossetic',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'pi',
            name: 'Pali',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'pag',
            name: 'Pangasinan',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'pa',
            name: 'Panjabi/Punjabi',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'pap',
            name: 'Papiamentu',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ps',
            name: 'Pashto',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'pdc',
            name: 'Pennsylvania German',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'fa',
            name: 'Persian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ff',
            name: 'Peul',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'pms',
            name: 'Piedmontese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'pl',
            name: 'Polish',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'pt',
            name: 'Portuguese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'qu',
            name: 'Quechua',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'rm',
            name: 'Raeto Romance',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ksh',
            name: 'Ripuarian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'rmy',
            name: 'Romani',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ro',
            name: 'Romanian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ru',
            name: 'Russian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'rw',
            name: 'Rwandi',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'sm',
            name: 'Samoan',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'bat-smg',
            name: 'Samogitian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'sg',
            name: 'Sango',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'sa',
            name: 'Sanskrit',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'sc',
            name: 'Sardinian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'sco',
            name: 'Scots',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'gd',
            name: 'Scottish Gaelic',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'sr',
            name: 'Serbian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'sh',
            name: 'Serbo-Croatian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'sn',
            name: 'Shona',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ii',
            name: 'Sichuan Yi',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'scn',
            name: 'Sicilian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'simple',
            name: 'Simple English',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'sd',
            name: 'Sindhi',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'si',
            name: 'Sinhalese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'sk',
            name: 'Slovak',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'sl',
            name: 'Slovenian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'so',
            name: 'Somalia',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'nr',
            name: 'South Ndebele',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'st',
            name: 'Southern Sotho',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'su',
            name: 'Sundanese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'sw',
            name: 'Swahili',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ss',
            name: 'Swati',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'sv',
            name: 'Swedish',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'tl',
            name: 'Tagalog',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ty',
            name: 'Tahitian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'tg',
            name: 'Tajik',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ta',
            name: 'Tamil',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'tt',
            name: 'Tatar',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'te',
            name: 'Telugu',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'tet',
            name: 'Tetum',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'th',
            name: 'Thai',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'bo',
            name: 'Tibetan',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ti',
            name: 'Tigrinya',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'tpi',
            name: 'Tok Pisin',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'to',
            name: 'Tonga',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ts',
            name: 'Tsonga',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'tn',
            name: 'Tswana',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'tum',
            name: 'Tumbuka',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'tr',
            name: 'Turkish',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'tk',
            name: 'Turkmen',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'tw',
            name: 'Twi',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'udm',
            name: 'Udmurt',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'uk',
            name: 'Ukrainian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ur',
            name: 'Urdu',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'ug',
            name: 'Uyghur',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'uz',
            name: 'Uzbek',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'uz_af',
            name: 'Uzbeki Afghanistan',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 've',
            name: 'Venda',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'vec',
            name: 'Venetian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'vi',
            name: 'Vietnamese',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'vo',
            name: 'Volapük',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'fiu-vro',
            name: 'Võro',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'wa',
            name: 'Walloon',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'war',
            name: 'Waray/Samar-Leyte Visayan',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'cy',
            name: 'Welsh',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'vls',
            name: 'West Flemish',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'fy',
            name: 'West Frisian',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'wo',
            name: 'Wolof',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'xh',
            name: 'Xhosa',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'yi',
            name: 'Yiddish',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'yo',
            name: 'Yoruba',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'za',
            name: 'Zhuang',
            isDeletable: true,
            isBasic: false
        },
        {
            code: 'zu',
            name: 'Zulu',
            isDeletable: true,
            isBasic: false
        }
    ];

    constructor (
        private http : HttpService
    ) {}

    uploadFile (file : File) : Observable<boolean> {
        const formData = new FormData();
        formData.append('file', file);

        return this.http.post('endpoint://faq.uploadFile', {
            body: formData,
            reportProgress: false
        }).pipe(
            take(1),
            map(response => response.status === 'OK'),
            catchError(error => {
                console.warn('uploadFile error:', error);
                return throwError(error);
            })
        );
    }
}
