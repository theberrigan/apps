from ...common import bfw
from ...common.types import *
from ...common.fns import splitSpaces, toInts, toFloats

from ..txd import Texture

from .consts import *
from .types import *

from bfw.utils import *



class Particles:
    def __init__ (self):
        self.particles : Opt[List['Particle']] = None

    def set (self, index : int, particle : 'Particle'):
        if self.particles is None:
            self.particles : List['Particle'] = [ None ] * PARTICLE_TYPE_COUNT

        self.particles[index] = particle

    def __iter__ (self):
        return iter(self.particles)


class Particle:
    def __init__ (self):
        self.type                       : TInt   = None  # see ParticleType
        self.name                       : TStr   = None
        self.renderColor                : TRGB   = None  # CRGBA     m_RenderColouring (u8)
        self.initColorVar               : TInt   = None  # uint8     m_InitialColorVariation
        self.fadeDestColor              : TRGB   = None  # CRGBA     m_FadeDestinationColor (u8)
        self.colorFadeTime              : TInt   = None  # uint32    m_ColorFadeTime
        self.defaultInitRadius          : TFloat = None  # float     m_fDefaultInitialRadius
        self.expansionRate              : TFloat = None  # float     m_fExpansionRate
        self.fadeToBlackInitIntensity   : TInt   = None  # uint8     m_nFadeToBlackInitialIntensity
        self.fadeToBlackTime            : TInt   = None  # int16     m_nFadeToBlackTime
        self.fadeToBlackAmount          : TInt   = None  # int16     m_nFadeToBlackAmount
        self.fadeAlphaInitIntensity     : TInt   = None  # uint8     m_nFadeAlphaInitialIntensity
        self.fadeAlphaTime              : TInt   = None  # int16     m_nFadeAlphaTime
        self.fadeAlphaAmount            : TInt   = None  # int16     m_nFadeAlphaAmount
        self.zRotationInitAngle         : TInt   = None  # uint16    m_nZRotationInitialAngle
        self.zRotationChangeTime        : TInt   = None  # uint16    m_nZRotationChangeTime
        self.zRotationAngleChangeAmount : TInt   = None  # int16     m_nZRotationAngleChangeAmount
        self.initZRadius                : TFloat = None  # float     m_fInitialZRadius
        self.zRadiusChangeTime          : TInt   = None  # uint16    m_nZRadiusChangeTime
        self.zRadiusChangeAmount        : TFloat = None  # float     m_fZRadiusChangeAmount
        self.animationSpeed             : TInt   = None  # uint16    m_nAnimationSpeed
        self.startAnimationFrame        : TInt   = None  # uint8     m_nStartAnimationFrame
        self.finalAnimationFrame        : TInt   = None  # uint8     m_nFinalAnimationFrame
        self.rotationSpeed              : TInt   = None  # uint16    m_nRotationSpeed
        self.gravitationalAcceleration  : TFloat = None  # float     m_fGravitationalAcceleration
        self.frictionDeceleration       : TInt   = None  # int32     m_nFrictionDecceleration
        self.lifeSpan                   : TInt   = None  # int32     m_nLifeSpan
        self.positionRandomError        : TFloat = None  # float     m_fPositionRandomError
        self.velocityRandomError        : TFloat = None  # float     m_fVelocityRandomError
        self.expansionRateError         : TFloat = None  # float     m_fExpansionRateError
        self.rotationRateError          : TInt   = None  # int32     m_nRotationRateError
        self.lifeSpanErrorShape         : TInt   = None  # uint32    m_nLifeSpanErrorShape
        self.trailLengthMultiplier      : TFloat = None  # float     m_fTrailLengthMultiplier
        self.textureStretch             : TVec   = None  # CVector2D m_vecTextureStretch
        self.windFactor                 : TFloat = None  # float     m_fWindFactor
        self.createRange                : TFloat = None  # float     m_fCreateRange
        self.flags                      : TInt   = None  # uint32    Flags

        self.frames : Opt[List[Texture]] = None  # Texture[] -- linked with textures using context


class ParticleReader:
    @classmethod
    def parseDefault (cls) -> Particles:
        return cls.fromFile(PARTICLES_FILE_PATH)

    @classmethod
    def fromFile (cls, filePath : str, ctx : Opt[Any] = None) -> Particles:
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        text = readText(filePath, encoding='utf-8')

        return cls().read(text, ctx)

    def read (self, text : str, ctx : Opt[Any] = None) -> Particles:
        particles = Particles()

        lines = text.split('\n')

        particleType = 0

        for line in lines:
            line = line.strip()

            if line == ';the end':
                break

            if not line or line[0] == ';':
                continue

            assert 0 <= particleType < PARTICLE_TYPE_COUNT, (particleType, line)

            values = splitSpaces(line)

            # --------------------------------------------------

            particle = Particle()

            particles.set(particleType, particle)

            particle.type                       = particleType
            particle.name                       = values[0].upper()
            particle.renderColor                = toInts(values[1:4])
            particle.initColorVar               = min(100, int(values[4]))
            particle.fadeDestColor              = toInts(values[5:8])
            particle.colorFadeTime              = int(values[8])
            particle.defaultInitRadius          = float(values[9])
            particle.expansionRate              = float(values[10])
            particle.fadeToBlackInitIntensity   = int(values[11])
            particle.fadeToBlackTime            = int(values[12])
            particle.fadeToBlackAmount          = int(values[13])
            particle.fadeAlphaInitIntensity     = int(values[14])
            particle.fadeAlphaTime              = int(values[15])
            particle.fadeAlphaAmount            = int(values[16])
            particle.zRotationInitAngle         = int(values[17])
            particle.zRotationChangeTime        = int(values[18])
            particle.zRotationAngleChangeAmount = int(values[19])
            particle.initZRadius                = float(values[20])
            particle.zRadiusChangeTime          = int(values[21])
            particle.zRadiusChangeAmount        = float(values[22])
            particle.animationSpeed             = int(values[23])
            particle.startAnimationFrame        = int(values[24])
            particle.finalAnimationFrame        = int(values[25])
            particle.rotationSpeed              = int(values[26])
            particle.gravitationalAcceleration  = float(values[27])
            particle.frictionDeceleration       = int(values[28])
            particle.lifeSpan                   = int(values[29])
            particle.positionRandomError        = float(values[30])
            particle.velocityRandomError        = float(values[31])
            particle.expansionRateError         = float(values[32])
            particle.rotationRateError          = float(values[33])  # TODO: in original parsed as int, but one value is 2.5
            particle.lifeSpanErrorShape         = int(values[34])
            particle.trailLengthMultiplier      = float(values[35])
            particle.textureStretch             = toFloats(values[36:38])
            particle.windFactor                 = float(values[38])
            particle.createRange                = float(values[39]) ** 2
            particle.flags                      = int(values[40])

            # --------------------------------------------------

            particleType += 1

        if ctx:
            self.linkWithTextures(particles, ctx)
        else:
            printW('Context is not provided, particles are not linked with texture frames')

        return particles

    def linkWithTextures (self, particles : Particles, ctx : Any):
        parMap = { p.type: p for p in particles }

        # game\src\renderer\Particle.cpp
        # link frames (textures) to particle data
        # rain drops implemented with shaders,and not with particles
        for item in PARTICLE_TYPES_TO_FRAMES:
            parTypes  = item['types']
            parFrames = item['frames']

            for parFrame in parFrames:
                tex = ctx.txd.particles.getTexture(parFrame)

                for parType in parTypes:
                    par : Particle = parMap[parType]

                    if par.frames is None:
                        par.frames = []

                    par.frames.append(tex)

        ''' 
        # NOTE:
        # These types don't have textures: GUNSMOKE, WATERDROP, BLOODDROP, HEATHAZE, HEATHAZE_IN_DIST
        
        # Unused loop
        for ( int32 i = 0; i < MAX_CARSPLASH_FILES; i++ ) {}
    
        # Unused textures mentioned in code
        gpFlame5Tex = RwTextureRead("flame5", nil);
        gpCloudTex1 = RwTextureRead("cloud3", nil);
        gpBulletHitTex = RwTextureRead("bullethitsmoke", nil);
        gpPointlightTex = RwTextureRead("pointlight", nil);
        gpDotTex = RwTextureRead("dot", nil);
        gpRainDripTex[0] = RwTextureRead("raindrip64", nil);
        gpRainDripTex[1] = RwTextureRead("raindripb64", nil);
        gpRainDripDarkTex[0] = RwTextureRead("raindrip64_d", nil);
        gpRainDripDarkTex[1] = RwTextureRead("raindripb64_d", nil);
        
        # Unused textures from particle.txd
        zonewhite64, lamp_shad_64, wincrack_32, walk_dont, goal, bullethitsmoke, white, reflection01, smoketrail, 
        outline3_64, outline2_64, outline_64, bloodpool_64, streek, cloudhilit, cloud3, cloud2, cloud1, newspaper01_64, 
        gameleaf02_64, particleskid, raindripb64_d, raindrip64_d, raindripb64, raindrip64, sandywater, waterreflection2, 
        waterwake, waterclear256, headlight, pointlight, dot, target256, shad_rcbaron, shad_exp, shad_bike, shad_heli, 
        shad_ped, shad_car, coronaringa, coronacircle, coronahex, coronaheadlightline, coronamoon, coronastar, 
        coronareflect, corona, flame5
        '''



def _test_ ():
    print(toJson(ParticleReader.parseDefault()))



__all__ = [
    'ParticleReader',
    'Particles',
    'Particle',

    '_test_',
]



if __name__ == '__main__':
    _test_()
