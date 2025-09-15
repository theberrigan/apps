from .types import BSPEntityFieldType



BSP_ENTITY_TYPES = {
    'DelayedUse': {
        'className': 'CBaseDelay'
    },
    'aiscripted_sequence': {
        'className': 'CCineAI'
    },
    'ambient_generic': {
        'className': 'CAmbientGeneric'
    },
    'ammo_357': {
        'className': 'CPythonAmmo'
    },
    'ammo_9mmAR': {
        'className': 'CMP5AmmoClip'
    },
    'ammo_9mmbox': {
        'className': 'CMP5Chainammo'
    },
    'ammo_9mmclip': {
        'className': 'CGlockAmmo'
    },
    'ammo_ARgrenades': {
        'className': 'CMP5AmmoGrenade'
    },
    'ammo_buckshot': {
        'className': 'CShotgunAmmo'
    },
    'ammo_crossbow': {
        'className': 'CCrossbowAmmo'
    },
    'ammo_egonclip': {
        'className': 'CEgonAmmo'
    },
    'ammo_gaussclip': {
        'className': 'CGaussAmmo'
    },
    'ammo_glockclip': {
        'className': 'CGlockAmmo'
    },
    'ammo_mp5clip': {
        'className': 'CMP5AmmoClip'
    },
    'ammo_mp5grenades': {
        'className': 'CMP5AmmoGrenade'
    },
    'ammo_rpgclip': {
        'className': 'CRpgAmmo'
    },
    'beam': {
        'className': 'CBeam'
    },
    'bmortar': {
        'className': 'CBMortar'
    },
    'bodyque': {
        'className': 'CCorpse'
    },
    'button_target': {
        'className': 'CButtonTarget'
    },
    'cine_blood': {
        'className': 'CCineBlood'
    },
    'controller_energy_ball': {
        'className': 'CControllerZapBall'
    },
    'controller_head_ball': {
        'className': 'CControllerHeadBall'
    },
    'crossbow_bolt': {
        'className': 'CCrossbowBolt'
    },
    'cycler': {
        'className': 'CGenericCycler'
    },
    'cycler_prdroid': {
        'className': 'CCyclerProbe'
    },
    'cycler_sprite': {
        'className': 'CCyclerSprite'
    },
    'cycler_weapon': {
        'className': 'CWeaponCycler'
    },
    'cycler_wreckage': {
        'className': 'CWreckage'
    },
    'env_beam': {
        'className': 'CLightning'
    },
    'env_beverage': {
        'className': 'CEnvBeverage'
    },
    'env_blood': {
        'className': 'CBlood'
    },
    'env_bubbles': {
        'className': 'CBubbling'
    },
    'env_debris': {
        'className': 'CEnvSpark'
    },
    'env_explosion': {
        'className': 'CEnvExplosion'
    },
    'env_fade': {
        'className': 'CFade'
    },
    'env_funnel': {
        'className': 'CEnvFunnel'
    },
    'env_global': {
        'className': 'CEnvGlobal'
    },
    'env_glow': {
        'className': 'CGlow'
    },
    'env_laser': {
        'className': 'CLaser'
    },
    'env_lightning': {
        'className': 'CLightning'
    },
    'env_message': {
        'className': 'CMessage'
    },
    'env_model': {
        'className': 'CCyclerSprite'
    },
    'env_render': {
        'className': 'CRenderFxManager'
    },
    'env_shake': {
        'className': 'CShake'
    },
    'env_shooter': {
        'className': 'CEnvShooter'
    },
    'env_smoker': {
        'className': 'CSmoker'
    },
    'env_sound': {
        'className': 'CEnvSound'
    },
    'env_spark': {
        'className': 'CEnvSpark'
    },
    'env_sprite': {
        'className': 'CSprite'
    },
    'fireanddie': {
        'className': 'CFireAndDie'
    },
    'func_breakable': {
        'className': 'CBreakable'
    },
    'func_button': {
        'className': 'CBaseButton'
    },
    'func_conveyor': {
        'className': 'CFuncConveyor'
    },
    'func_door': {
        'className': 'CBaseDoor'
    },
    'func_door_rotating': {
        'className': 'CRotDoor'
    },
    'func_friction': {
        'className': 'CFrictionModifier'
    },
    'func_guntarget': {
        'className': 'CGunTarget'
    },
    'func_healthcharger': {
        'className': 'CWallHealth'
    },
    'func_illusionary': {
        'className': 'CFuncIllusionary'
    },
    'func_ladder': {
        'className': 'CLadder'
    },
    'func_monsterclip': {
        'className': 'CFuncMonsterClip'
    },
    'func_mortar_field': {
        'className': 'CFuncMortarField'
    },
    'func_pendulum': {
        'className': 'CPendulum'
    },
    'func_plat': {
        'className': 'CFuncPlat'
    },
    'func_platrot': {
        'className': 'CFuncPlatRot'
    },
    'func_pushable': {
        'className': 'CPushable'
    },
    'func_recharge': {
        'className': 'CRecharge'
    },
    'func_rot_button': {
        'className': 'CRotButton'
    },
    'func_rotating': {
        'className': 'CFuncRotating'
    },
    'func_tank': {
        'className': 'CFuncTankGun'
    },
    'func_tankcontrols': {
        'className': 'CFuncTankControls'
    },
    'func_tanklaser': {
        'className': 'CFuncTankLaser'
    },
    'func_tankmortar': {
        'className': 'CFuncTankMortar'
    },
    'func_tankrocket': {
        'className': 'CFuncTankRocket'
    },
    'func_trackautochange': {
        'className': 'CFuncTrackAuto'
    },
    'func_trackchange': {
        'className': 'CFuncTrackChange'
    },
    'func_tracktrain': {
        'className': 'CFuncTrackTrain'
    },
    'func_train': {
        'className': 'CFuncTrain'
    },
    'func_traincontrols': {
        'className': 'CFuncTrainControls'
    },
    'func_wall': {
        'className': 'CFuncWall'
    },
    'func_wall_toggle': {
        'className': 'CFuncWallToggle'
    },
    'func_water': {
        'className': 'CBaseDoor'
    },
    'game_counter': {
        'className': 'CGameCounter'
    },
    'game_counter_set': {
        'className': 'CGameCounterSet'
    },
    'game_end': {
        'className': 'CGameEnd'
    },
    'game_player_equip': {
        'className': 'CGamePlayerEquip'
    },
    'game_player_hurt': {
        'className': 'CGamePlayerHurt'
    },
    'game_player_team': {
        'className': 'CGamePlayerTeam'
    },
    'game_score': {
        'className': 'CGameScore'
    },
    'game_team_master': {
        'className': 'CGameTeamMaster'
    },
    'game_team_set': {
        'className': 'CGameTeamSet'
    },
    'game_text': {
        'className': 'CGameText'
    },
    'game_zone_player': {
        'className': 'CGamePlayerZone'
    },
    'garg_stomp': {
        'className': 'CStomp'
    },
    'gibshooter': {
        'className': 'CGibShooter'
    },
    'grenade': {
        'className': 'CGrenade'
    },
    'hornet': {
        'className': 'CHornet'
    },
    'hvr_rocket': {
        'className': 'CApacheHVR'
    },
    'info_bigmomma': {
        'className': 'CInfoBM'
    },
    'info_intermission': {
        'className': 'CInfoIntermission'
    },
    'info_landmark': {
        'className': 'CPointEntity'
    },
    'info_node': {
        'className': 'CNodeEnt'
    },
    'info_node_air': {
        'className': 'CNodeEnt'
    },
    'info_null': {
        'className': 'CNullEntity'
    },
    'info_player_deathmatch': {
        'className': 'CBaseDMStart'
    },
    'info_player_start': {
        'className': 'CPointEntity'
    },
    'info_target': {
        'className': 'CPointEntity'
    },
    'info_teleport_destination': {
        'className': 'CPointEntity'
    },
    'infodecal': {
        'className': 'CDecal'
    },
    'item_airtank': {
        'className': 'CAirtank'
    },
    'item_antidote': {
        'className': 'CItemAntidote'
    },
    'item_battery': {
        'className': 'CItemBattery'
    },
    'item_healthkit': {
        'className': 'CHealthKit'
    },
    'item_longjump': {
        'className': 'CItemLongJump'
    },
    'item_security': {
        'className': 'CItemSecurity'
    },
    'item_sodacan': {
        'className': 'CItemSoda'
    },
    'item_suit': {
        'className': 'CItemSuit'
    },
    'laser_spot': {
        'className': 'CLaserSpot'
    },
    'light': {
        'className': 'CLight'
    },
    'light_environment': {
        'className': 'CEnvLight'
    },
    'light_spot': {
        'className': 'CLight'
    },
    'mapClassName': {
        'className': 'DLLClassName'
    },
    'momentary_door': {
        'className': 'CMomentaryDoor'
    },
    'momentary_rot_button': {
        'className': 'CMomentaryRotButton'
    },
    'monster_alien_controller': {
        'className': 'CController'
    },
    'monster_alien_grunt': {
        'className': 'CAGrunt'
    },
    'monster_alien_slave': {
        'className': 'CISlave'
    },
    'monster_apache': {
        'className': 'CApache'
    },
    'monster_babycrab': {
        'className': 'CBabyCrab'
    },
    'monster_barnacle': {
        'className': 'CBarnacle'
    },
    'monster_barney': {
        'className': 'CBarney'
    },
    'monster_barney_dead': {
        'className': 'CDeadBarney'
    },
    'monster_bigmomma': {
        'className': 'CBigMomma'
    },
    'monster_bloater': {
        'className': 'CBloater'
    },
    'monster_bullchicken': {
        'className': 'CBullsquid'
    },
    'monster_cine2_hvyweapons': {
        'className': 'CCine2HeavyWeapons'
    },
    'monster_cine2_scientist': {
        'className': 'CCine2Scientist'
    },
    'monster_cine2_slave': {
        'className': 'CCine2Slave'
    },
    'monster_cine3_barney': {
        'className': 'CCine3Barney'
    },
    'monster_cine3_scientist': {
        'className': 'CCine3Scientist'
    },
    'monster_cine_barney': {
        'className': 'CCineBarney'
    },
    'monster_cine_panther': {
        'className': 'CCinePanther'
    },
    'monster_cine_scientist': {
        'className': 'CCineScientist'
    },
    'monster_cockroach': {
        'className': 'CRoach'
    },
    'monster_flyer': {
        'className': 'CFlockingFlyer'
    },
    'monster_flyer_flock': {
        'className': 'CFlockingFlyerFlock'
    },
    'monster_furniture': {
        'className': 'CFurniture'
    },
    'monster_gargantua': {
        'className': 'CGargantua'
    },
    'monster_generic': {
        'className': 'CGenericMonster'
    },
    'monster_gman': {
        'className': 'CGMan'
    },
    'monster_grunt_repel': {
        'className': 'CHGruntRepel'
    },
    'monster_headcrab': {
        'className': 'CHeadCrab'
    },
    'monster_hevsuit_dead': {
        'className': 'CDeadHEV'
    },
    'monster_hgrunt_dead': {
        'className': 'CDeadHGrunt'
    },
    'monster_houndeye': {
        'className': 'CHoundeye'
    },
    'monster_human_assassin': {
        'className': 'CHAssassin'
    },
    'monster_human_grunt': {
        'className': 'CHGrunt'
    },
    'monster_ichthyosaur': {
        'className': 'CIchthyosaur'
    },
    'monster_leech': {
        'className': 'CLeech'
    },
    'monster_miniturret': {
        'className': 'CMiniTurret'
    },
    'monster_mortar': {
        'className': 'CMortar'
    },
    'monster_nihilanth': {
        'className': 'CNihilanth'
    },
    'monster_osprey': {
        'className': 'COsprey'
    },
    'monster_player': {
        'className': 'CPlayerMonster'
    },
    'monster_rat': {
        'className': 'CRat'
    },
    'monster_satchel': {
        'className': 'CSatchelCharge'
    },
    'monster_scientist': {
        'className': 'CScientist'
    },
    'monster_scientist_dead': {
        'className': 'CDeadScientist'
    },
    'monster_sentry': {
        'className': 'CSentry'
    },
    'monster_sitting_scientist': {
        'className': 'CSittingScientist'
    },
    'monster_snark': {
        'className': 'CSqueakGrenade'
    },
    'monster_tentacle': {
        'className': 'CTentacle'
    },
    'monster_tentaclemaw': {
        'className': 'CTentacleMaw'
    },
    'monster_tripmine': {
        'className': 'CTripmineGrenade'
    },
    'monster_turret': {
        'className': 'CTurret'
    },
    'monster_vortigaunt': {
        'className': 'CISlave'
    },
    'monster_zombie': {
        'className': 'CZombie'
    },
    'monstermaker': {
        'className': 'CMonsterMaker'
    },
    'multi_manager': {
        'className': 'CMultiManager'
    },
    'multisource': {
        'className': 'CMultiSource'
    },
    'my_monster': {
        'className': 'CMyMonster'
    },
    'nihilanth_energy_ball': {
        'className': 'CNihilanthHVR'
    },
    'node_viewer': {
        'className': 'CNodeViewer'
    },
    'node_viewer_fly': {
        'className': 'CNodeViewer'
    },
    'node_viewer_human': {
        'className': 'CNodeViewer'
    },
    'node_viewer_large': {
        'className': 'CNodeViewer'
    },
    'path_corner': {
        'className': 'CPathCorner'
    },
    'path_track': {
        'className': 'CPathTrack'
    },
    'player': {
        'className': 'CBasePlayer'
    },
    'player_loadsaved': {
        'className': 'CRevertSaved'
    },
    'player_weaponstrip': {
        'className': 'CStripWeapons'
    },
    'rpg_rocket': {
        'className': 'CRpgRocket'
    },
    'scripted_sentence': {
        'className': 'CScriptedSentence'
    },
    'scripted_sequence': {
        'className': 'CCineMonster'
    },
    'soundent': {
        'className': 'CSoundEnt'
    },
    'spark_shower': {
        'className': 'CShower'
    },
    'speaker': {
        'className': 'CSpeaker'
    },
    'squidspit': {
        'className': 'CSquidSpit'
    },
    'streak_spiral': {
        'className': 'CSpiral'
    },
    'target_cdaudio': {
        'className': 'CTargetCDAudio'
    },
    'test_effect': {
        'className': 'CTestEffect'
    },
    'testhull': {
        'className': 'CTestHull'
    },
    'trigger': {
        'className': 'CBaseTrigger'
    },
    'trigger_auto': {
        'className': 'CAutoTrigger'
    },
    'trigger_autosave': {
        'className': 'CTriggerSave'
    },
    'trigger_camera': {
        'className': 'CTriggerCamera'
    },
    'trigger_cdaudio': {
        'className': 'CTriggerCDAudio'
    },
    'trigger_changelevel': {
        'className': 'CChangeLevel'
    },
    'trigger_changetarget': {
        'className': 'CTriggerChangeTarget'
    },
    'trigger_counter': {
        'className': 'CTriggerCounter'
    },
    'trigger_endsection': {
        'className': 'CTriggerEndSection'
    },
    'trigger_gravity': {
        'className': 'CTriggerGravity'
    },
    'trigger_hurt': {
        'className': 'CTriggerHurt'
    },
    'trigger_monsterjump': {
        'className': 'CTriggerMonsterJump'
    },
    'trigger_multiple': {
        'className': 'CTriggerMultiple'
    },
    'trigger_once': {
        'className': 'CTriggerOnce'
    },
    'trigger_push': {
        'className': 'CTriggerPush'
    },
    'trigger_relay': {
        'className': 'CTriggerRelay'
    },
    'trigger_teleport': {
        'className': 'CTriggerTeleport'
    },
    'trigger_transition': {
        'className': 'CTriggerVolume'
    },
    'trip_beam': {
        'className': 'CTripBeam'
    },
    'weapon_357': {
        'className': 'CPython'
    },
    'weapon_9mmAR': {
        'className': 'CMP5'
    },
    'weapon_9mmhandgun': {
        'className': 'CGlock'
    },
    'weapon_crossbow': {
        'className': 'CCrossbow'
    },
    'weapon_crowbar': {
        'className': 'CCrowbar'
    },
    'weapon_egon': {
        'className': 'CEgon'
    },
    'weapon_gauss': {
        'className': 'CGauss'
    },
    'weapon_glock': {
        'className': 'CGlock'
    },
    'weapon_handgrenade': {
        'className': 'CHandGrenade'
    },
    'weapon_hornetgun': {
        'className': 'CHgun'
    },
    'weapon_mp5': {
        'className': 'CMP5'
    },
    'weapon_python': {
        'className': 'CPython'
    },
    'weapon_rpg': {
        'className': 'CRpg'
    },
    'weapon_satchel': {
        'className': 'CSatchel'
    },
    'weapon_shotgun': {
        'className': 'CShotgun'
    },
    'weapon_snark': {
        'className': 'CSqueak'
    },
    'weapon_tripmine': {
        'className': 'CTripmine'
    },
    'weaponbox': {
        'className': 'CWeaponBox'
    },
    'world_items': {
        'className': 'CWorldItem'
    },
    'worldspawn': {
        'className': 'CWorld'
    },
    'xen_hair': {
        'className': 'CXenHair'
    },
    'xen_hull': {
        'className': 'CXenHull'
    },
    'xen_plantlight': {
        'className': 'CXenPLight'
    },
    'xen_spore_large': {
        'className': 'CXenSporeLarge'
    },
    'xen_spore_medium': {
        'className': 'CXenSporeMed'
    },
    'xen_spore_small': {
        'className': 'CXenSporeSmall'
    },
    'xen_tree': {
        'className': 'CXenTree'
    },
    'xen_ttrigger': {
        'className': 'CXenTreeTrigger'
    }
}

BSP_ENTITY_FIELDS = {
    'absmax': {
        'type': BSPEntityFieldType.PosVec
    },
    'absmin': {
        'type': BSPEntityFieldType.PosVec
    },
    'aiment': {
        'type': BSPEntityFieldType.EDict
    },
    'air_finished': {
        'type': BSPEntityFieldType.Time
    },
    'angles': {
        'type': BSPEntityFieldType.Vec
    },
    'animtime': {
        'type': BSPEntityFieldType.Time
    },
    'armortype': {
        'type': BSPEntityFieldType.Float
    },
    'armorvalue': {
        'type': BSPEntityFieldType.Float
    },
    'avelocity': {
        'type': BSPEntityFieldType.Vec
    },
    'basevelocity': {
        'type': BSPEntityFieldType.Vec
    },
    'blending': {
        'type': BSPEntityFieldType.Integer
    },
    'body': {
        'type': BSPEntityFieldType.Integer
    },
    'button': {
        'type': BSPEntityFieldType.Integer
    },
    'chain': {
        'type': BSPEntityFieldType.EDict
    },
    'classname': {
        'type': BSPEntityFieldType.String
    },
    'colormap': {
        'type': BSPEntityFieldType.Integer
    },
    'controller': {
        'type': BSPEntityFieldType.Integer
    },
    'deadflag': {
        'type': BSPEntityFieldType.Float
    },
    'dmg': {
        'type': BSPEntityFieldType.Float
    },
    'dmg_inflictor': {
        'type': BSPEntityFieldType.EDict
    },
    'dmg_save': {
        'type': BSPEntityFieldType.Float
    },
    'dmg_take': {
        'type': BSPEntityFieldType.Float
    },
    'dmgtime': {
        'type': BSPEntityFieldType.Time
    },
    'effects': {
        'type': BSPEntityFieldType.Integer
    },
    'enemy': {
        'type': BSPEntityFieldType.EDict
    },
    'fixangle': {
        'type': BSPEntityFieldType.Float
    },
    'flags': {
        'type': BSPEntityFieldType.Float
    },
    'frags': {
        'type': BSPEntityFieldType.Float
    },
    'frame': {
        'type': BSPEntityFieldType.Float
    },
    'framerate': {
        'type': BSPEntityFieldType.Float
    },
    'friction': {
        'type': BSPEntityFieldType.Float
    },
    'globalname': {
        'type': BSPEntityFieldType.String
    },
    'gravity': {
        'type': BSPEntityFieldType.Float
    },
    'groundentity': {
        'type': BSPEntityFieldType.EDict
    },
    'health': {
        'type': BSPEntityFieldType.Float
    },
    'ideal_yaw': {
        'type': BSPEntityFieldType.Float
    },
    'idealpitch': {
        'type': BSPEntityFieldType.Float
    },
    'impulse': {
        'type': BSPEntityFieldType.Integer
    },
    'light_level': {
        'type': BSPEntityFieldType.Float
    },
    'ltime': {
        'type': BSPEntityFieldType.Time
    },
    'max_health': {
        'type': BSPEntityFieldType.Float
    },
    'maxs': {
        'type': BSPEntityFieldType.Vec
    },
    'message': {
        'type': BSPEntityFieldType.String
    },
    'mins': {
        'type': BSPEntityFieldType.Vec
    },
    'model': {
        'type': BSPEntityFieldType.ModelName
    },
    'modelindex': {
        'type': BSPEntityFieldType.Integer
    },
    'movedir': {
        'type': BSPEntityFieldType.Vec
    },
    'movetype': {
        'type': BSPEntityFieldType.Integer
    },
    'netname': {
        'type': BSPEntityFieldType.String
    },
    'nextthink': {
        'type': BSPEntityFieldType.Time
    },
    'noise': {
        'type': BSPEntityFieldType.SoundName
    },
    'noise1': {
        'type': BSPEntityFieldType.SoundName
    },
    'noise2': {
        'type': BSPEntityFieldType.SoundName
    },
    'noise3': {
        'type': BSPEntityFieldType.SoundName
    },
    'oldorigin': {
        'type': BSPEntityFieldType.PosVec
    },
    'origin': {
        'type': BSPEntityFieldType.PosVec
    },
    'owner': {
        'type': BSPEntityFieldType.EDict
    },
    'pain_finished': {
        'type': BSPEntityFieldType.Time
    },
    'pitch_speed': {
        'type': BSPEntityFieldType.Float
    },
    'punchangle': {
        'type': BSPEntityFieldType.Vec
    },
    'radsuit_finished': {
        'type': BSPEntityFieldType.Time
    },
    'renderamt': {
        'type': BSPEntityFieldType.Float
    },
    'rendercolor': {
        'type': BSPEntityFieldType.Vec
    },
    'renderfx': {
        'type': BSPEntityFieldType.Integer
    },
    'rendermode': {
        'type': BSPEntityFieldType.Integer
    },
    'scale': {
        'type': BSPEntityFieldType.Float
    },
    'sequence': {
        'type': BSPEntityFieldType.Integer
    },
    'size': {
        'type': BSPEntityFieldType.Vec
    },
    'skin': {
        'type': BSPEntityFieldType.Integer
    },
    'solid': {
        'type': BSPEntityFieldType.Integer
    },
    'spawnflags': {
        'type': BSPEntityFieldType.Integer
    },
    'speed': {
        'type': BSPEntityFieldType.Float
    },
    'takedamage': {
        'type': BSPEntityFieldType.Float
    },
    'target': {
        'type': BSPEntityFieldType.String
    },
    'targetname': {
        'type': BSPEntityFieldType.String
    },
    'team': {
        'type': BSPEntityFieldType.Integer
    },
    'teleport_time': {
        'type': BSPEntityFieldType.Time
    },
    'v_angle': {
        'type': BSPEntityFieldType.Vec
    },
    'velocity': {
        'type': BSPEntityFieldType.Vec
    },
    'view_ofs': {
        'type': BSPEntityFieldType.Vec
    },
    'viewmodel': {
        'type': BSPEntityFieldType.ModelName
    },
    'waterlevel': {
        'type': BSPEntityFieldType.Integer
    },
    'watertype': {
        'type': BSPEntityFieldType.Integer
    },
    'weaponmodel': {
        'type': BSPEntityFieldType.ModelName
    },
    'weapons': {
        'type': BSPEntityFieldType.Integer
    },
    'yaw_speed': {
        'type': BSPEntityFieldType.Float
    }
}



__all__ = [
    'BSP_ENTITY_TYPES',
    'BSP_ENTITY_FIELDS',
]