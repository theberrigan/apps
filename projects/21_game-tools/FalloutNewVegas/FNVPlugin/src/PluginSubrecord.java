// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import java.util.Iterator;
import java.util.List;
import java.util.HashMap;
import java.util.Map;

public class PluginSubrecord extends SerializedElement
{
    private String subrecordType;
    private byte[] subrecordData;
    private static Map<String, SubrecordInfo> typeMap;
    private static Map<Integer, FunctionInfo> functionMap;
    private static final int[] offsetRepeating4;
    private static final int[] offsetRepeating8;
    private static final int[] offsetRepeating12;
    private static final int[] offsetZero;
    private static final int[] offsetFour;
    private static final int[] offsetTwelve;
    private static final int[] offsetSixteen;
    private static final int[] offsetThirtysix;
    private static final int[] offsetZeroFour;
    private static final int[] offsetZeroEight;
    private static final int[] offsetFourEight;
    private static final int[] offsetEightTwelve;
    private static final int[] offsetEightSixteen;
    private static final int[] offsetBPND;
    private static final int[] offsetCSNODATA;
    private static final int[] offsetMGEFDATA;
    private static final int[] offsetEFSHDATA;
    private static final int[] offsetEXPLDATA;
    private static final int[] offsetPROJDATA;
    private static final SubrecordInfo[] subrecordInfo;
    private static final FunctionInfo[] functionInfo;
    
    public PluginSubrecord(final SerializedElement parent, final String subrecordType, final byte[] subrecordData) {
        super(parent);
        this.subrecordType = subrecordType;
        this.subrecordData = subrecordData;
        if (PluginSubrecord.typeMap == null) {
            PluginSubrecord.typeMap = new HashMap<String, SubrecordInfo>(PluginSubrecord.subrecordInfo.length);
            for (final SubrecordInfo info : PluginSubrecord.subrecordInfo) {
                final String infoType = info.getSubrecordType();
                info.setSubrecordChain(PluginSubrecord.typeMap.get(infoType));
                PluginSubrecord.typeMap.put(infoType, info);
            }
        }
        if (PluginSubrecord.functionMap == null) {
            PluginSubrecord.functionMap = new HashMap<Integer, FunctionInfo>(PluginSubrecord.functionInfo.length);
            for (final FunctionInfo info2 : PluginSubrecord.functionInfo) {
                PluginSubrecord.functionMap.put(new Integer(info2.getCode()), info2);
            }
        }
    }
    
    public String getSubrecordType() {
        return this.subrecordType;
    }
    
    public byte[] getSubrecordData() {
        return this.subrecordData;
    }
    
    public void setSubrecordData(final byte[] subrecordData) {
        this.subrecordData = subrecordData;
    }
    
    public int[][] getReferences() {
        int[][] references = null;
        final PluginRecord parentRecord = (PluginRecord)this.getParent();
        final String recordType = parentRecord.getRecordType();
        if (this.subrecordType.equals("CTDA")) {
            int index = 0;
            final int functionCode = SerializedElement.getInteger(this.subrecordData, 8);
            final FunctionInfo functionInfo = PluginSubrecord.functionMap.get(new Integer(functionCode));
            if (functionInfo != null) {
                references = new int[3][2];
                if (functionInfo.getName().equals("GetVATSValue")) {
                    final int type = SerializedElement.getInteger(this.subrecordData, 12);
                    if (type == 0 || type == 1 || type == 2 || type == 3 || type == 9 || type == 10) {
                        references[index][0] = 16;
                        references[index][1] = SerializedElement.getInteger(this.subrecordData, 16);
                        ++index;
                    }
                }
                else {
                    if (functionInfo.isFirstReference() && this.subrecordData.length >= 16) {
                        references[index][0] = 12;
                        references[index][1] = SerializedElement.getInteger(this.subrecordData, 12);
                        ++index;
                    }
                    if (functionInfo.isSecondReference() && this.subrecordData.length >= 20) {
                        references[index][0] = 16;
                        references[index][1] = SerializedElement.getInteger(this.subrecordData, 16);
                        ++index;
                    }
                }
            }
            if (this.subrecordData.length >= 28) {
                final int type = SerializedElement.getInteger(this.subrecordData, 20);
                if (type == 2) {
                    if (references == null) {
                        references = new int[1][2];
                    }
                    references[index][0] = 24;
                    references[index][1] = SerializedElement.getInteger(this.subrecordData, 24);
                }
            }
        }
        else if (this.subrecordType.equals("COED")) {
            if (this.subrecordData.length >= 8) {
                int refID = SerializedElement.getInteger(this.subrecordData, 0);
                if (refID != 0) {
                    references = new int[2][2];
                    references[0][0] = 0;
                    references[0][1] = refID;
                    refID = SerializedElement.getInteger(this.subrecordData, 4);
                    if (refID > 10) {
                        references[1][0] = 4;
                        references[1][1] = refID;
                    }
                }
            }
        }
        else if (this.subrecordType.equals("MODS") || this.subrecordType.equals("MO2S") || this.subrecordType.equals("MO3S") || this.subrecordType.equals("MO4S")) {
            int dataLength = this.subrecordData.length;
            if (dataLength >= 4) {
                final int count = SerializedElement.getInteger(this.subrecordData, 0);
                dataLength -= 4;
                int dataOffset = 4;
                references = new int[count][2];
                for (int i = 0; i < count; ++i) {
                    if (dataLength < 4) {
                        break;
                    }
                    final int stringLength = SerializedElement.getInteger(this.subrecordData, dataOffset);
                    dataOffset += 4 + stringLength;
                    dataLength -= 4 + stringLength;
                    if (dataLength < 4) {
                        break;
                    }
                    references[i][0] = dataOffset;
                    references[i][1] = SerializedElement.getInteger(this.subrecordData, dataOffset);
                    dataOffset += 8;
                    dataLength -= 8;
                }
            }
        }
        else if (recordType.equals("NOTE") && this.subrecordType.equals("TNAM")) {
            int noteType = -1;
            final List<PluginSubrecord> subrecordList = parentRecord.getSubrecords();
            for (final PluginSubrecord prevSubrecord : subrecordList) {
                if (prevSubrecord.getSubrecordType().equals("DATA")) {
                    noteType = prevSubrecord.getSubrecordData()[0];
                    break;
                }
            }
            if (noteType == 3) {
                references = new int[1][2];
                references[0][0] = 0;
                references[0][1] = SerializedElement.getInteger(this.subrecordData, 0);
            }
        }
        else if (recordType.equals("PERK") && this.subrecordType.equals("DATA")) {
            final List<PluginSubrecord> subrecordList2 = parentRecord.getSubrecords();
            final int index2 = subrecordList2.indexOf(this);
            if (index2 > 0) {
                final PluginSubrecord prevSubrecord2 = subrecordList2.get(index2 - 1);
                if (prevSubrecord2.getSubrecordType().equals("PRKE")) {
                    final int type = prevSubrecord2.getSubrecordData()[0];
                    if (type == 0 || type == 1) {
                        references = new int[1][2];
                        references[0][0] = 0;
                        references[0][1] = SerializedElement.getInteger(this.subrecordData, 0);
                    }
                }
            }
        }
        else if (recordType.equals("NAVI") && this.subrecordType.equals("NVCI")) {
            int size = 1;
            int count2;
            for (int offset = 4, j = 0; j < 3 && offset + 4 <= this.subrecordData.length; offset += (count2 + 1) * 4, ++j) {
                count2 = SerializedElement.getInteger(this.subrecordData, offset);
                size += count2;
            }
            references = new int[size][2];
            references[0][0] = 0;
            references[0][1] = SerializedElement.getInteger(this.subrecordData, 0);
            int offset = 4;
            int index3 = 1;
            for (int i = 0; i < 3 && offset + 4 <= this.subrecordData.length; ++i) {
                final int count3 = SerializedElement.getInteger(this.subrecordData, offset);
                offset += 4;
                for (int k = 0; k < count3 && offset + 4 <= this.subrecordData.length; offset += 4, ++k) {
                    references[index3][0] = offset;
                    references[index3][1] = SerializedElement.getInteger(this.subrecordData, offset);
                    ++index3;
                }
            }
        }
        else if (recordType.equals("NAVM") && this.subrecordType.equals("NVEX")) {
            final int count4 = this.subrecordData.length / 10;
            if (count4 > 0) {
                references = new int[count4][2];
                for (int index2 = 0; index2 < count4; ++index2) {
                    final int offset2 = index2 * 10 + 4;
                    references[index2][0] = offset2;
                    references[index2][1] = SerializedElement.getInteger(this.subrecordData, offset2);
                }
            }
        }
        else if (recordType.equals("CLMT") && this.subrecordType.equals("WLST")) {
            final int count4 = this.subrecordData.length / 12;
            if (count4 > 0) {
                references = new int[2 * count4][2];
                for (int index2 = 0; index2 < count4; ++index2) {
                    final int offset2 = index2 * 12;
                    references[2 * index2][0] = offset2;
                    references[2 * index2][1] = SerializedElement.getInteger(this.subrecordData, offset2);
                    references[2 * index2 + 1][0] = offset2 + 8;
                    references[2 * index2 + 1][1] = SerializedElement.getInteger(this.subrecordData, offset2 + 8);
                }
            }
        }
        else if (recordType.equals("PACK") && (this.subrecordType.equals("PLDT") || this.subrecordType.equals("PLD2"))) {
            final int type2 = SerializedElement.getInteger(this.subrecordData, 0);
            if (type2 == 0 || type2 == 1 || type2 == 4) {
                references = new int[1][2];
                references[0][0] = 4;
                references[0][1] = SerializedElement.getInteger(this.subrecordData, 4);
            }
        }
        else if (recordType.equals("PACK") && (this.subrecordType.equals("PTDT") || this.subrecordType.equals("PTD2"))) {
            final int type2 = SerializedElement.getInteger(this.subrecordData, 0);
            if (type2 == 0 || type2 == 1) {
                references = new int[1][2];
                references[0][0] = 4;
                references[0][1] = SerializedElement.getInteger(this.subrecordData, 4);
            }
        }
        else {
            boolean returnReferences = false;
            SubrecordInfo subrecordInfo;
            for (subrecordInfo = PluginSubrecord.typeMap.get(this.subrecordType); subrecordInfo != null; subrecordInfo = subrecordInfo.getSubrecordChain()) {
                final String[] recordTypes = subrecordInfo.getRecordTypes();
                for (int i = 0; i < recordTypes.length; ++i) {
                    if (recordType.equals(recordTypes[i])) {
                        returnReferences = true;
                        break;
                    }
                }
                if (returnReferences) {
                    break;
                }
            }
            if (returnReferences) {
                final int[] refOffsets = subrecordInfo.getReferenceOffsets();
                int l = -1;
                int index4 = 0;
                boolean repeating;
                int refSize;
                int refOffset;
                if (refOffsets[0] < 0) {
                    repeating = true;
                    refSize = -refOffsets[0];
                    refOffset = -refSize;
                    references = new int[this.subrecordData.length / refSize][2];
                }
                else {
                    repeating = false;
                    refOffset = 0;
                    refSize = 4;
                    references = new int[refOffsets.length][2];
                }
                while (true) {
                    if (repeating) {
                        refOffset += refSize;
                    }
                    else {
                        if (++l == refOffsets.length) {
                            break;
                        }
                        refOffset = refOffsets[l];
                    }
                    if (refOffset + refSize > this.subrecordData.length) {
                        break;
                    }
                    references[index4][0] = refOffset;
                    references[index4][1] = SerializedElement.getInteger(this.subrecordData, refOffset);
                    ++index4;
                }
            }
        }
        return references;
    }
    
    @Override
    public boolean equals(final Object object) {
        boolean areEqual = false;
        if (object instanceof PluginSubrecord) {
            final PluginSubrecord objSubrecord = (PluginSubrecord)object;
            if (objSubrecord.getSubrecordType().equals(this.subrecordType)) {
                final byte[] objSubrecordData = objSubrecord.getSubrecordData();
                if (objSubrecordData.length == this.subrecordData.length && SerializedElement.compareArrays(this.subrecordData, 0, objSubrecordData, 0, this.subrecordData.length) == 0) {
                    areEqual = true;
                }
            }
        }
        return areEqual;
    }
    
    @Override
    public String toString() {
        String desc;
        if (this.subrecordType.charAt(0) < ' ') {
            desc = String.format("%02X%02X%02X%02X subrecord", (int)this.subrecordType.charAt(0), (int)this.subrecordType.charAt(1), (int)this.subrecordType.charAt(2), (int)this.subrecordType.charAt(3));
        }
        else {
            desc = this.subrecordType + " subrecord";
        }
        return desc;
    }
    
    @Override
    public Object clone() {
        final Object clonedObject = super.clone();
        final PluginSubrecord clonedSubrecord = (PluginSubrecord)clonedObject;
        final int length = this.subrecordData.length;
        clonedSubrecord.subrecordData = new byte[length];
        System.arraycopy(this.subrecordData, 0, clonedSubrecord.subrecordData, 0, length);
        return clonedObject;
    }
    
    static {
        offsetRepeating4 = new int[] { -4 };
        offsetRepeating8 = new int[] { -8 };
        offsetRepeating12 = new int[] { -12 };
        offsetZero = new int[] { 0 };
        offsetFour = new int[] { 4 };
        offsetTwelve = new int[] { 12 };
        offsetSixteen = new int[] { 16 };
        offsetThirtysix = new int[] { 36 };
        offsetZeroFour = new int[] { 0, 4 };
        offsetZeroEight = new int[] { 0, 8 };
        offsetFourEight = new int[] { 4, 8 };
        offsetEightTwelve = new int[] { 8, 12 };
        offsetEightSixteen = new int[] { 8, 16 };
        offsetBPND = new int[] { 12, 16, 32, 36, 68, 72 };
        offsetCSNODATA = new int[] { 44, 48 };
        offsetMGEFDATA = new int[] { 8, 24, 32, 36, 40, 44, 48, 52 };
        offsetEFSHDATA = new int[] { 244 };
        offsetEXPLDATA = new int[] { 12, 16, 28, 32 };
        offsetPROJDATA = new int[] { 16, 20, 36, 40, 56, 60, 64 };
        subrecordInfo = new SubrecordInfo[] { new SubrecordInfo("\u0000IAD", PluginSubrecord.offsetZero, new String[] { "WTHR" }), new SubrecordInfo("\u0001IAD", PluginSubrecord.offsetZero, new String[] { "WTHR" }), new SubrecordInfo("\u0002IAD", PluginSubrecord.offsetZero, new String[] { "WTHR" }), new SubrecordInfo("\u0003IAD", PluginSubrecord.offsetZero, new String[] { "WTHR" }), new SubrecordInfo("ANAM", PluginSubrecord.offsetRepeating4, new String[] { "CPTH", "DOOR", "IDLE", "INFO" }), new SubrecordInfo("ATXT", PluginSubrecord.offsetZero, new String[] { "LAND" }), new SubrecordInfo("BIPL", PluginSubrecord.offsetZero, new String[] { "ARMO", "WEAP" }), new SubrecordInfo("BNAM", PluginSubrecord.offsetZero, new String[] { "DOOR" }), new SubrecordInfo("BPND", PluginSubrecord.offsetBPND, new String[] { "BPTD" }), new SubrecordInfo("BTXT", PluginSubrecord.offsetZero, new String[] { "LAND" }), new SubrecordInfo("CARD", PluginSubrecord.offsetZero, new String[] { "CDCK" }), new SubrecordInfo("CNAM", PluginSubrecord.offsetZero, new String[] { "CREA", "NPC_", "PACK", "WRLD" }), new SubrecordInfo("CNTO", PluginSubrecord.offsetZero, new String[] { "CONT", "CREA", "NPC_" }), new SubrecordInfo("CRDT", PluginSubrecord.offsetTwelve, new String[] { "WEAP" }), new SubrecordInfo("CSCR", PluginSubrecord.offsetZero, new String[] { "CREA" }), new SubrecordInfo("CSDI", PluginSubrecord.offsetZero, new String[] { "CREA" }), new SubrecordInfo("DATA", PluginSubrecord.offsetZero, new String[] { "ANIO", "ECZN", "NAVM" }), new SubrecordInfo("Data", PluginSubrecord.offsetCSNODATA, new String[] { "CSNO" }), new SubrecordInfo("DATA", PluginSubrecord.offsetEFSHDATA, new String[] { "EFSH" }), new SubrecordInfo("DATA", PluginSubrecord.offsetEXPLDATA, new String[] { "EXPL" }), new SubrecordInfo("DATA", PluginSubrecord.offsetRepeating4, new String[] { "IPDS" }), new SubrecordInfo("DATA", PluginSubrecord.offsetMGEFDATA, new String[] { "MGEF" }), new SubrecordInfo("DATA", PluginSubrecord.offsetPROJDATA, new String[] { "PROJ" }), new SubrecordInfo("DATA", PluginSubrecord.offsetFour, new String[] { "DEHY", "HUNG", "RADS", "SLPD" }), new SubrecordInfo("DATA", PluginSubrecord.offsetEightTwelve, new String[] { "RCPE" }), new SubrecordInfo("DNAM", PluginSubrecord.offsetZero, new String[] { "IPCT" }), new SubrecordInfo("DNAM", PluginSubrecord.offsetFour, new String[] { "PWAT" }), new SubrecordInfo("DNAM", PluginSubrecord.offsetThirtysix, new String[] { "WEAP" }), new SubrecordInfo("DSTD", PluginSubrecord.offsetEightTwelve, new String[] { "ALCH", "ACTI", "BOOK", "CREA", "DOOR", "KEYM", "MSTT", "PROJ", "TACT", "WEAP" }), new SubrecordInfo("EFID", PluginSubrecord.offsetZero, new String[] { "ALCH", "ENCH", "INGR", "SPEL" }), new SubrecordInfo("EFSD", PluginSubrecord.offsetZero, new String[] { "WEAP" }), new SubrecordInfo("EITM", PluginSubrecord.offsetZero, new String[] { "ARMO", "CREA", "EXPL", "NPC_", "WEAP" }), new SubrecordInfo("ENAM", PluginSubrecord.offsetZero, new String[] { "NPC_" }), new SubrecordInfo("ENIT", PluginSubrecord.offsetEightSixteen, new String[] { "ALCH" }), new SubrecordInfo("GNAM", PluginSubrecord.offsetZero, new String[] { "ALOC" }), new SubrecordInfo("GNAM", PluginSubrecord.offsetRepeating4, new String[] { "LTEX", "WATR" }), new SubrecordInfo("HNAM", PluginSubrecord.offsetZero, new String[] { "ALOC", "HDPT", "MSET", "NPC_" }), new SubrecordInfo("IDLA", PluginSubrecord.offsetRepeating4, new String[] { "IDLM" }), new SubrecordInfo("IMPS", PluginSubrecord.offsetFourEight, new String[] { "WRLD" }), new SubrecordInfo("INAM", PluginSubrecord.offsetZero, new String[] { "ACHR", "ACRE", "CREA", "MESG", "MSET", "NPC_", "PACK", "PGRE", "REFR", "TERM", "WEAP", "WRLD" }), new SubrecordInfo("KNAM", PluginSubrecord.offsetZero, new String[] { "INFO" }), new SubrecordInfo("LNAM", PluginSubrecord.offsetZero, new String[] { "CREA", "INFO", "FLST", "LSCR" }), new SubrecordInfo("LTMP", PluginSubrecord.offsetZero, new String[] { "CELL" }), new SubrecordInfo("LVLG", PluginSubrecord.offsetZero, new String[] { "LVLI" }), new SubrecordInfo("LVLO", PluginSubrecord.offsetFour, new String[] { "LVLC", "LVLI", "LVLN" }), new SubrecordInfo("MNAM", PluginSubrecord.offsetZero, new String[] { "CAMS", "EXPL" }), new SubrecordInfo("NAME", PluginSubrecord.offsetZero, new String[] { "ACHR", "ACRE", "INFO", "PGRE", "REFR" }), new SubrecordInfo("NAM0", PluginSubrecord.offsetZero, new String[] { "QUST", "WEAP" }), new SubrecordInfo("NAM2", PluginSubrecord.offsetZero, new String[] { "WRLD" }), new SubrecordInfo("NAM3", PluginSubrecord.offsetZero, new String[] { "WRLD" }), new SubrecordInfo("NAM6", PluginSubrecord.offsetZero, new String[] { "WEAP" }), new SubrecordInfo("NAM7", PluginSubrecord.offsetZero, new String[] { "WEAP" }), new SubrecordInfo("NAM8", PluginSubrecord.offsetZero, new String[] { "WEAP" }), new SubrecordInfo("NAM9", PluginSubrecord.offsetZero, new String[] { "WEAP" }), new SubrecordInfo("NVDP", PluginSubrecord.offsetRepeating8, new String[] { "NAVM" }), new SubrecordInfo("NVMI", PluginSubrecord.offsetFourEight, new String[] { "NAVI" }), new SubrecordInfo("ONAM", PluginSubrecord.offsetZero, new String[] { "NOTE", "RACE", "SCOL" }), new SubrecordInfo("PKDD", PluginSubrecord.offsetFour, new String[] { "PACK" }), new SubrecordInfo("PKID", PluginSubrecord.offsetZero, new String[] { "CREA", "NPC_" }), new SubrecordInfo("PNAM", PluginSubrecord.offsetZero, new String[] { "CREA", "INFO", "NPC_", "TERM" }), new SubrecordInfo("QNAM", PluginSubrecord.offsetZero, new String[] { "CONT" }), new SubrecordInfo("QSTA", PluginSubrecord.offsetZero, new String[] { "QUST" }), new SubrecordInfo("QSTI", PluginSubrecord.offsetZero, new String[] { "DIAL", "INFO" }), new SubrecordInfo("QSTR", PluginSubrecord.offsetZero, new String[] { "DIAL" }), new SubrecordInfo("RAGA", PluginSubrecord.offsetZero, new String[] { "BPTD" }), new SubrecordInfo("RCIL", PluginSubrecord.offsetZero, new String[] { "RCPE" }), new SubrecordInfo("RCOD", PluginSubrecord.offsetZero, new String[] { "RCPE" }), new SubrecordInfo("RDAT", PluginSubrecord.offsetZero, new String[] { "ASPC" }), new SubrecordInfo("RDGS", PluginSubrecord.offsetZero, new String[] { "REGN" }), new SubrecordInfo("RDOT", PluginSubrecord.offsetZero, new String[] { "REGN" }), new SubrecordInfo("RDSD", PluginSubrecord.offsetRepeating12, new String[] { "REGN" }), new SubrecordInfo("RDWT", PluginSubrecord.offsetZeroEight, new String[] { "REGN" }), new SubrecordInfo("REPL", PluginSubrecord.offsetZero, new String[] { "ARMO", "WEAP" }), new SubrecordInfo("RNAM", PluginSubrecord.offsetZero, new String[] { "ACTI", "ALOC", "NPC_" }), new SubrecordInfo("SCRI", PluginSubrecord.offsetZero, new String[] { "ACTI", "ALCH", "ARMO", "BOOK", "CCRD", "CHAL", "COBJ", "CONT", "CREA", "DOOR", "FURN", "INGR", "KEYM", "LIGH", "MISC", "NPC_", "QUST", "TACT", "TERM", "WEAP" }), new SubrecordInfo("SCRO", PluginSubrecord.offsetZero, new String[] { "ACHR", "ACRE", "INFO", "PACK", "PERK", "PGRE", "REFR", "QUST", "SCPT", "TERM" }), new SubrecordInfo("SNAM", PluginSubrecord.offsetZero, new String[] { "ASPC", "ACTI", "ADDN", "CONT", "CPTH", "CREA", "DOOR", "INFO", "IPCT", "LIGH", "MSTT", "NPC_", "NOTE", "TACT", "TERM", "WATR", "WEAP", "WTHR" }), new SubrecordInfo("SNDD", PluginSubrecord.offsetZero, new String[] { "INFO" }), new SubrecordInfo("SPLO", PluginSubrecord.offsetZero, new String[] { "CREA", "NPC_" }), new SubrecordInfo("TCLF", PluginSubrecord.offsetZero, new String[] { "INFO" }), new SubrecordInfo("TCLT", PluginSubrecord.offsetZero, new String[] { "INFO" }), new SubrecordInfo("TNAM", PluginSubrecord.offsetZero, new String[] { "ACHR", "ACRE", "LTEX", "PACK", "PGRE", "REFR", "RGDL", "TERM", "WEAP" }), new SubrecordInfo("TPIC", PluginSubrecord.offsetZero, new String[] { "INFO" }), new SubrecordInfo("TPLT", PluginSubrecord.offsetZero, new String[] { "CREA", "NPC_" }), new SubrecordInfo("TRDT", PluginSubrecord.offsetSixteen, new String[] { "INFO" }), new SubrecordInfo("UNAM", PluginSubrecord.offsetZero, new String[] { "WEAP" }), new SubrecordInfo("VNAM", PluginSubrecord.offsetZero, new String[] { "ACTI", "TACT" }), new SubrecordInfo("VTCK", PluginSubrecord.offsetZero, new String[] { "CREA", "NPC_" }), new SubrecordInfo("WNAM", PluginSubrecord.offsetZero, new String[] { "ACTI", "REGN", "WEAP", "WRLD" }), new SubrecordInfo("WMI1", PluginSubrecord.offsetZero, new String[] { "WEAP" }), new SubrecordInfo("WMI2", PluginSubrecord.offsetZero, new String[] { "WEAP" }), new SubrecordInfo("WMI3", PluginSubrecord.offsetZero, new String[] { "WEAP" }), new SubrecordInfo("WNM1", PluginSubrecord.offsetZero, new String[] { "WEAP" }), new SubrecordInfo("WNM2", PluginSubrecord.offsetZero, new String[] { "WEAP" }), new SubrecordInfo("WNM3", PluginSubrecord.offsetZero, new String[] { "WEAP" }), new SubrecordInfo("XAMT", PluginSubrecord.offsetZero, new String[] { "REFR" }), new SubrecordInfo("XAPR", PluginSubrecord.offsetZero, new String[] { "ACHR", "ACRE", "PGRE", "REFR" }), new SubrecordInfo("XCAS", PluginSubrecord.offsetZero, new String[] { "CELL" }), new SubrecordInfo("XCCM", PluginSubrecord.offsetZero, new String[] { "CELL" }), new SubrecordInfo("XCIM", PluginSubrecord.offsetZero, new String[] { "CELL" }), new SubrecordInfo("XCLR", PluginSubrecord.offsetRepeating4, new String[] { "CELL" }), new SubrecordInfo("XCMO", PluginSubrecord.offsetZero, new String[] { "CELL" }), new SubrecordInfo("XCWT", PluginSubrecord.offsetZero, new String[] { "CELL" }), new SubrecordInfo("XDCR", PluginSubrecord.offsetZero, new String[] { "ACHR", "ACRE", "PGRE", "REFR" }), new SubrecordInfo("XEMI", PluginSubrecord.offsetZero, new String[] { "ACHR", "ACRE", "PGRE", "REFR" }), new SubrecordInfo("XESP", PluginSubrecord.offsetZero, new String[] { "ACHR", "ACRE", "PGRE", "REFR" }), new SubrecordInfo("XEZN", PluginSubrecord.offsetZero, new String[] { "ACHR", "ACRE", "CELL", "PGRE", "REFR", "WRLD" }), new SubrecordInfo("XLOC", PluginSubrecord.offsetFour, new String[] { "REFR" }), new SubrecordInfo("XLKR", PluginSubrecord.offsetZero, new String[] { "ACHR", "ACRE", "PGRE", "REFR" }), new SubrecordInfo("XLRM", PluginSubrecord.offsetZero, new String[] { "REFR" }), new SubrecordInfo("XLTW", PluginSubrecord.offsetZero, new String[] { "REFR" }), new SubrecordInfo("XMBR", PluginSubrecord.offsetZero, new String[] { "ACHR", "ACRE", "PGRE", "REFR" }), new SubrecordInfo("XMRC", PluginSubrecord.offsetZero, new String[] { "ACHR", "ACRE" }), new SubrecordInfo("XNAM", PluginSubrecord.offsetZero, new String[] { "ALOC", "FACT", "RACE", "RGDL", "WATR", "WEAP" }), new SubrecordInfo("XNDP", PluginSubrecord.offsetZero, new String[] { "REFR" }), new SubrecordInfo("XOWN", PluginSubrecord.offsetZero, new String[] { "ACHR", "ACRE", "CELL", "PGRE", "REFR" }), new SubrecordInfo("XPOD", PluginSubrecord.offsetRepeating4, new String[] { "REFR" }), new SubrecordInfo("XPWR", PluginSubrecord.offsetZero, new String[] { "PGRE", "REFR" }), new SubrecordInfo("XRDO", PluginSubrecord.offsetTwelve, new String[] { "REFR" }), new SubrecordInfo("XTEL", PluginSubrecord.offsetZero, new String[] { "REFR" }), new SubrecordInfo("XTRG", PluginSubrecord.offsetZero, new String[] { "REFR" }), new SubrecordInfo("YNAM", PluginSubrecord.offsetZero, new String[] { "ALCH", "ALOC", "AMMO", "ARMO", "COBJ", "KEYM", "MISC", "NOTE", "RACE", "WEAP" }), new SubrecordInfo("ZNAM", PluginSubrecord.offsetZero, new String[] { "ALCH", "ALOC", "AMMO", "ARMO", "COBJ", "CREA", "KEYM", "MISC", "NPC_", "NOTE", "WEAP", "WRLD" }) };
        functionInfo = new FunctionInfo[] { new FunctionInfo("Exists", 415, true, false), new FunctionInfo("GetCrime", 122, true, false), new FunctionInfo("GetDeadCount", 84, true, false), new FunctionInfo("GetDetected", 45, true, false), new FunctionInfo("GetDetectionLevel", 180, true, false), new FunctionInfo("GetDisposition", 76, true, false), new FunctionInfo("GetDistance", 1, true, false), new FunctionInfo("GetEquipped", 182, true, false), new FunctionInfo("GetFactionCombatReaction", 411, true, true), new FunctionInfo("GetFactionRank", 73, true, false), new FunctionInfo("GetFactionRankDifference", 60, true, true), new FunctionInfo("GetFactionRelation", 450, true, false), new FunctionInfo("GetGlobalValue", 74, true, false), new FunctionInfo("GetHasNote", 382, true, false), new FunctionInfo("GetHeadingAngle", 99, true, false), new FunctionInfo("GetInCell", 67, true, false), new FunctionInfo("GetInCellParam", 230, true, true), new FunctionInfo("GetInFaction", 71, true, false), new FunctionInfo("GetInSameCell", 32, true, false), new FunctionInfo("GetInWorldspace", 310, true, false), new FunctionInfo("GetInZone", 446, true, false), new FunctionInfo("GetIsClass", 68, true, false), new FunctionInfo("GetIsClassDefault", 228, true, false), new FunctionInfo("GetIsCurrentPackage", 161, true, false), new FunctionInfo("GetIsCurrentWeather", 149, true, false), new FunctionInfo("GetIsID", 72, true, false), new FunctionInfo("GetIsRace", 69, true, false), new FunctionInfo("GetIsReference", 136, true, false), new FunctionInfo("GetIsUsedItem", 246, true, false), new FunctionInfo("GetIsVoiceType", 427, true, false), new FunctionInfo("GetItemCount", 47, true, false), new FunctionInfo("GetLineOfSight", 27, true, false), new FunctionInfo("GetPCEnemyOfFaction", 197, true, false), new FunctionInfo("GetPCExpelled", 193, true, false), new FunctionInfo("GetPCFactionAttack", 199, true, false), new FunctionInfo("GetPCFactionMurder", 195, true, false), new FunctionInfo("GetPCInFaction", 132, true, false), new FunctionInfo("GetPCIsClass", 129, true, false), new FunctionInfo("GetPCIsRace", 130, true, false), new FunctionInfo("GetQuestCompleted", 546, true, false), new FunctionInfo("GetQuestRunning", 56, true, false), new FunctionInfo("GetQuestVariable", 79, true, false), new FunctionInfo("GetScriptVariable", 53, true, false), new FunctionInfo("GetShouldAttack", 66, true, false), new FunctionInfo("GetSpellUsageNum", 555, true, false), new FunctionInfo("GetStage", 58, true, false), new FunctionInfo("GetStageDone", 59, true, false), new FunctionInfo("GetTalkedToPCParam", 172, true, false), new FunctionInfo("GetThreatRatio", 478, true, false), new FunctionInfo("GetVATSBackAreaFree", 520, true, false), new FunctionInfo("GetVATSBackTargetVisible", 527, true, false), new FunctionInfo("GetVATSFrontAreaFree", 521, true, false), new FunctionInfo("GetVATSFrontTargetVisible", 528, true, false), new FunctionInfo("GetVATSLeftAreaFree", 519, true, false), new FunctionInfo("GetVATSLeftTargetVisible", 526, true, false), new FunctionInfo("GetVATSRightAreaFree", 518, true, false), new FunctionInfo("GetVATSRightTargetVisible", 525, true, false), new FunctionInfo("GetVATSValue", 408, false, true), new FunctionInfo("HasMagicEffect", 214, true, false), new FunctionInfo("HasPerk", 449, true, false), new FunctionInfo("IsCellOwner", 280, true, true), new FunctionInfo("IsCombatTarget", 515, true, false), new FunctionInfo("IsCurrentFurnitureObj", 163, true, false), new FunctionInfo("IsCurrentFurnitureRef", 162, true, false), new FunctionInfo("IsKiller", 409, true, false), new FunctionInfo("IsKillerObject", 410, true, false), new FunctionInfo("IsInList", 372, true, false), new FunctionInfo("IsLastIdlePlayed", 451, true, false), new FunctionInfo("IsOwner", 278, true, false), new FunctionInfo("IsPlayerGrabbedRef", 464, true, false), new FunctionInfo("IsSpellTarget", 223, true, false), new FunctionInfo("IsTalkingActivatorActor", 370, true, false), new FunctionInfo("IsWeaponInList", 399, true, false), new FunctionInfo("SameFaction", 42, true, false), new FunctionInfo("SameRace", 43, true, false), new FunctionInfo("SameSex", 44, true, false) };
    }
}
