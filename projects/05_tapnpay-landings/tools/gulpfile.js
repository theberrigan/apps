const fs = require('fs');
const path = require('path');
const yargs = require('yargs/yargs');
const gulp = require('gulp');
const gulpif = require('gulp-if');
const sass = require('gulp-sass')(require('sass'));
const rename = require('gulp-rename');
const sourcemaps = require('gulp-sourcemaps');
const postcss = require('gulp-postcss');
const postcssCssVariables = require('postcss-css-variables');
const postcssCalc = require('postcss-calc');
const postcssDiscardDuplicates = require('postcss-discard-duplicates');
const autoprefixer = require('autoprefixer');
const ts = require('gulp-typescript');

const { argv } = yargs(process.argv.slice(2));
const { page, mode } = argv;
const isDev = mode === 'development';  // production

process.env.NODE_ENV = process.env.ENV = mode;

const allSCSSGlob = '../assets/**/*.scss';
const allTSGlob = '../assets/ts/**/*.ts';
const scssInputFile = `../assets/scss/${ page }.scss`;
const cssOutputDir = '../assets/css/';
const tsInputFile = `../assets/ts/${ page }.ts`;
const jsOutputDir = '../assets/js/';

const tsProject = ts.createProject({
    noImplicitAny: false,
    module: 'commonjs',
    target: 'es2018',
    lib: [ 'dom', 'es6', 'es2018' ],
    allowJs: true,
});


function compileSCSS () {
    return gulp.src(scssInputFile)
        .pipe(gulpif(isDev, sourcemaps.init()))
        .pipe(sass().on('error', sass.logError))
        .pipe(postcss([
            postcssCssVariables({
                preserve: false,
                preserveAtRulesOrder: true
            }),
            postcssCalc({
                precision: 0
            }),
            postcssDiscardDuplicates,
            autoprefixer(),
        ]))
        .pipe(rename({
            extname: '.css'
        }))
        .pipe(gulpif(isDev, sourcemaps.write()))
        .pipe(gulp.dest(cssOutputDir));
}

function compileTS () {
    return gulp.src(tsInputFile)
        .pipe(gulpif(isDev, sourcemaps.init()))
        .pipe(tsProject())
        .pipe(rename({
            extname: '.js'
        }))
        .pipe(gulpif(isDev, sourcemaps.write()))
        .pipe(gulp.dest(jsOutputDir));
}

exports.build = gulp.parallel(compileSCSS, compileTS);

exports.watch = function () {
    gulp.watch(allSCSSGlob, { ignoreInitial: false }, compileSCSS);    
    gulp.watch(allTSGlob, { ignoreInitial: false }, compileTS);
};
