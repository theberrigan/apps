// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import java.util.ListIterator;
import java.util.Iterator;
import java.util.HashMap;
import java.io.IOException;
import java.util.zip.DataFormatException;
import java.io.RandomAccessFile;
import java.io.File;
import java.util.ArrayList;
import java.util.Map;
import java.util.List;

public class PluginGroup extends SerializedElement
{
    public static final int TOP = 0;
    public static final int WORLDSPACE = 1;
    public static final int INTERIOR_BLOCK = 2;
    public static final int INTERIOR_SUBBLOCK = 3;
    public static final int EXTERIOR_BLOCK = 4;
    public static final int EXTERIOR_SUBBLOCK = 5;
    public static final int CELL = 6;
    public static final int TOPIC = 7;
    public static final int CELL_PERSISTENT = 8;
    public static final int CELL_TEMPORARY = 9;
    public static final int CELL_DISTANT = 10;
    private byte[] groupLabel;
    private String groupRecordType;
    private int groupParentID;
    private int groupType;
    private byte[] timestamp;
    private int formVersion;
    private List<SerializedElement> recordList;
    private static Map<String, String> typeMap;
    private static String[][] groupDescriptions;
    
    public PluginGroup(final SerializedElement parent, final String recordType) {
        super(parent);
        this.groupType = 0;
        this.groupLabel = recordType.getBytes();
        this.groupRecordType = recordType;
        this.timestamp = new byte[4];
        this.formVersion = 0;
        this.recordList = new ArrayList<SerializedElement>();
        if (PluginGroup.typeMap == null) {
            this.buildTypeMap();
        }
    }
    
    public PluginGroup(final SerializedElement parent, final int groupType, final byte[] groupLabel) {
        super(parent);
        this.groupType = groupType;
        this.groupLabel = groupLabel;
        this.timestamp = new byte[4];
        this.formVersion = 0;
        switch (groupType) {
            case 0: {
                if (groupLabel[0] >= 32) {
                    this.groupRecordType = new String(groupLabel);
                    break;
                }
                this.groupRecordType = new String();
                break;
            }
            case 1:
            case 6:
            case 7:
            case 8:
            case 9:
            case 10: {
                this.groupParentID = SerializedElement.getInteger(groupLabel, 0);
                break;
            }
        }
        this.recordList = new ArrayList<SerializedElement>();
        if (PluginGroup.typeMap == null) {
            this.buildTypeMap();
        }
    }
    
    public PluginGroup(final SerializedElement parent, final int groupType, final int groupParentID) {
        super(parent);
        this.groupType = groupType;
        SerializedElement.setInteger(groupParentID, this.groupLabel = new byte[4], 0);
        this.timestamp = new byte[4];
        this.formVersion = 0;
        switch (groupType) {
            case 1:
            case 6:
            case 7:
            case 8:
            case 9:
            case 10: {
                this.groupParentID = groupParentID;
                break;
            }
        }
        this.recordList = new ArrayList<SerializedElement>();
        if (PluginGroup.typeMap == null) {
            this.buildTypeMap();
        }
    }
    
    public PluginGroup(final SerializedElement parent, final File file, final RandomAccessFile in, final byte[] groupPrefix) throws DataFormatException, IOException, PluginException {
        super(parent);
        if (groupPrefix.length != 24) {
            throw new IllegalArgumentException("The group prefix is not 24 bytes");
        }
        int dataLength = SerializedElement.getInteger(groupPrefix, 4);
        if (dataLength < 24) {
            throw new PluginException(file.getName() + ": Group length is less than 24 bytes");
        }
        dataLength -= 24;
        System.arraycopy(groupPrefix, 8, this.groupLabel = new byte[4], 0, 4);
        this.groupType = SerializedElement.getInteger(groupPrefix, 12);
        System.arraycopy(groupPrefix, 16, this.timestamp = new byte[4], 0, 4);
        this.formVersion = SerializedElement.getInteger(groupPrefix, 20);
        switch (this.groupType) {
            case 0: {
                if (this.groupLabel[0] >= 32) {
                    this.groupRecordType = new String(this.groupLabel);
                    break;
                }
                this.groupRecordType = new String();
                break;
            }
            case 1:
            case 6:
            case 7:
            case 8:
            case 9:
            case 10: {
                this.groupParentID = SerializedElement.getInteger(this.groupLabel, 0);
                break;
            }
        }
        this.recordList = new ArrayList<SerializedElement>();
        if (PluginGroup.typeMap == null) {
            this.buildTypeMap();
        }
        final byte[] prefix = new byte[24];
        while (dataLength >= 24) {
            final int count = in.read(prefix);
            if (count != 24) {
                throw new PluginException(file.getName() + ": Group pecord prefix is incomplete");
            }
            dataLength -= 24;
            final String type = new String(prefix, 0, 4);
            int length = SerializedElement.getInteger(prefix, 4);
            SerializedElement element;
            if (type.equals("GRUP")) {
                length -= 24;
                element = new PluginGroup(this, file, in, prefix);
            }
            else {
                element = new PluginRecord(this, file, in, prefix);
            }
            this.recordList.add(element);
            dataLength -= length;
        }
        if (dataLength == 0) {
            return;
        }
        if (this.groupType == 0) {
            throw new PluginException(file.getName() + ": Group " + this.groupRecordType + " is incomplete");
        }
        throw new PluginException(file.getName() + ": Subgroup type " + this.groupType + " is incomplete");
    }
    
    private void buildTypeMap() {
        PluginGroup.typeMap = new HashMap<String, String>(PluginGroup.groupDescriptions.length);
        for (int i = 0; i < PluginGroup.groupDescriptions.length; ++i) {
            PluginGroup.typeMap.put(PluginGroup.groupDescriptions[i][0], PluginGroup.groupDescriptions[i][1]);
        }
    }
    
    public int getRecordCount() {
        int recordCount = 0;
        for (final SerializedElement element : this.recordList) {
            ++recordCount;
            if (element instanceof PluginGroup) {
                recordCount += ((PluginGroup)element).getRecordCount();
            }
        }
        return recordCount;
    }
    
    public boolean isEmpty() {
        return this.recordList.size() == 0;
    }
    
    public int getGroupType() {
        return this.groupType;
    }
    
    public byte[] getGroupLabel() {
        return this.groupLabel;
    }
    
    public void setGroupLabel(final byte[] label) {
        this.groupLabel = label;
        switch (this.groupType) {
            case 0: {
                if (this.groupLabel[0] >= 32) {
                    this.groupRecordType = new String(this.groupLabel);
                    break;
                }
                this.groupRecordType = new String();
                break;
            }
            case 1:
            case 6:
            case 7:
            case 8:
            case 9:
            case 10: {
                this.groupParentID = SerializedElement.getInteger(this.groupLabel, 0);
                break;
            }
        }
    }
    
    public String getGroupRecordType() {
        return this.groupRecordType;
    }
    
    public int getGroupParentID() {
        return this.groupParentID;
    }
    
    public void setGroupParentID(final int parentID) {
        SerializedElement.setInteger(this.groupParentID = parentID, this.groupLabel, 0);
    }
    
    public List<SerializedElement> getRecordList() {
        return this.recordList;
    }
    
    public int updateMappings(final List<PluginRecord> pluginRecordList, final Map<Integer, PluginRecord> formIDMap) throws PluginException {
        int recordCount = 0;
        for (final SerializedElement element : this.recordList) {
            ++recordCount;
            if (element instanceof PluginGroup) {
                recordCount += ((PluginGroup)element).updateMappings(pluginRecordList, formIDMap);
            }
            else {
                final PluginRecord record = (PluginRecord)element;
                final int formID = record.getFormID();
                final Integer mapFormID = new Integer(formID);
                final String editorID = record.getEditorID();
                if (formID == 0) {
                    throw new PluginException(String.format("Zero form ID found for %s record %s", record.getRecordType(), editorID));
                }
                if (formIDMap.get(mapFormID) != null) {
                    throw new PluginException(String.format("Duplicate form ID %08X found for %s record %s", mapFormID, record.getRecordType(), editorID));
                }
                pluginRecordList.add(record);
                formIDMap.put(mapFormID, record);
            }
        }
        return recordCount;
    }
    
    public void removeIgnoredRecords(final List<PluginRecord> pluginRecordList, final Map<Integer, PluginRecord> formIDMap) {
        final ListIterator<SerializedElement> lit = this.recordList.listIterator();
        boolean keepGroup = false;
        while (lit.hasNext()) {
            final SerializedElement element = lit.next();
            if (element instanceof PluginGroup) {
                final PluginGroup group = (PluginGroup)element;
                final int groupType = group.getGroupType();
                if (groupType == 1 || groupType == 6 || groupType == 7) {
                    if (!keepGroup) {
                        group.removeGroupRecords(pluginRecordList, formIDMap);
                        lit.remove();
                    }
                    else {
                        group.removeIgnoredRecords(pluginRecordList, formIDMap);
                    }
                }
                else {
                    group.removeIgnoredRecords(pluginRecordList, formIDMap);
                    if (group.isEmpty()) {
                        lit.remove();
                    }
                }
                keepGroup = false;
            }
            else {
                final PluginRecord record = (PluginRecord)element;
                keepGroup = false;
                if (record.isIgnored()) {
                    lit.remove();
                    pluginRecordList.remove(record);
                    formIDMap.remove(new Integer(record.getFormID()));
                }
                else {
                    final String recordType = record.getRecordType();
                    if (!recordType.equals("WRLD") && !recordType.equals("CELL") && !recordType.equals("DIAL")) {
                        continue;
                    }
                    keepGroup = true;
                }
            }
        }
    }
    
    public void removeGroupRecords(final List<PluginRecord> pluginRecordList, final Map<Integer, PluginRecord> formIDMap) {
        for (final SerializedElement element : this.recordList) {
            if (element instanceof PluginGroup) {
                final PluginGroup group = (PluginGroup)element;
                group.removeGroupRecords(pluginRecordList, formIDMap);
            }
            else {
                final PluginRecord record = (PluginRecord)element;
                pluginRecordList.remove(record);
                formIDMap.remove(new Integer(record.getFormID()));
            }
        }
    }
    
    public void store(final RandomAccessFile out) throws DataFormatException, IOException {
        final byte[] prefix = new byte[24];
        final long groupPosition = out.getFilePointer();
        out.write(prefix);
        for (final SerializedElement element : this.recordList) {
            if (element instanceof PluginGroup) {
                ((PluginGroup)element).store(out);
            }
            else {
                ((PluginRecord)element).store(out);
            }
        }
        final long stopPosition = out.getFilePointer();
        System.arraycopy("GRUP".getBytes(), 0, prefix, 0, 4);
        SerializedElement.setInteger((int)(stopPosition - groupPosition), prefix, 4);
        System.arraycopy(this.groupLabel, 0, prefix, 8, 4);
        SerializedElement.setInteger(this.groupType, prefix, 12);
        System.arraycopy(this.timestamp, 0, prefix, 16, 4);
        SerializedElement.setInteger(this.formVersion, prefix, 20);
        out.seek(groupPosition);
        out.write(prefix);
        out.seek(stopPosition);
    }
    
    @Override
    public int hashCode() {
        return SerializedElement.getInteger(this.groupLabel, 0) + (this.groupType << 24) + this.recordList.size();
    }
    
    @Override
    public boolean equals(final Object object) {
        boolean areEqual = false;
        if (object instanceof PluginGroup) {
            final PluginGroup objGroup = (PluginGroup)object;
            if (objGroup.getGroupType() == this.groupType) {
                final byte[] objGroupLabel = objGroup.getGroupLabel();
                if (SerializedElement.compareArrays(this.groupLabel, 0, objGroupLabel, 0, 4) == 0) {
                    final List<SerializedElement> objRecordList = objGroup.getRecordList();
                    if (objRecordList.size() == this.recordList.size()) {
                        areEqual = true;
                        for (int i = 0; i < this.recordList.size(); ++i) {
                            if (!objRecordList.get(i).equals(this.recordList.get(i))) {
                                areEqual = false;
                                break;
                            }
                        }
                    }
                }
            }
        }
        return areEqual;
    }
    
    @Override
    public String toString() {
        final int intValue = SerializedElement.getInteger(this.groupLabel, 0);
        String text = null;
        switch (this.groupType) {
            case 0: {
                final String type = new String(this.groupLabel);
                final String description = PluginGroup.typeMap.get(type);
                if (description != null) {
                    text = String.format("Group: %s", description);
                    break;
                }
                text = String.format("Group: Type %s", new String(this.groupLabel));
                break;
            }
            case 1: {
                text = String.format("Group: Worldspace (%08X) children", intValue);
                break;
            }
            case 2: {
                text = String.format("Group: Interior cell block %d", intValue);
                break;
            }
            case 3: {
                text = String.format("Group: Interior cell subblock %d", intValue);
                break;
            }
            case 4: {
                int x = intValue >>> 16;
                if ((x & 0x8000) != 0x0) {
                    x |= 0xFFFF0000;
                }
                int y = intValue & 0xFFFF;
                if ((y & 0x8000) != 0x0) {
                    y |= 0xFFFF0000;
                }
                text = String.format("Group: Exterior cell block %d,%d", x, y);
                break;
            }
            case 5: {
                int x = intValue >>> 16;
                if ((x & 0x8000) != 0x0) {
                    x |= 0xFFFF0000;
                }
                int y = intValue & 0xFFFF;
                if ((y & 0x8000) != 0x0) {
                    y |= 0xFFFF0000;
                }
                text = String.format("Group: Exterior cell subblock %d,%d", x, y);
                break;
            }
            case 6: {
                text = String.format("Group: Cell (%08X) children", intValue);
                break;
            }
            case 7: {
                text = String.format("Group: Topic (%08X) children", intValue);
                break;
            }
            case 8: {
                text = String.format("Group: Cell (%08X) persistent children", intValue);
                break;
            }
            case 9: {
                text = String.format("Group: Cell (%08X) temporary children", intValue);
                break;
            }
            case 10: {
                text = String.format("Group: Cell (%08X) visible distant children", intValue);
                break;
            }
            default: {
                text = String.format("Group: Type %d, Parent %08X", this.groupType, intValue);
                break;
            }
        }
        return text;
    }
    
    @Override
    public Object clone() {
        final Object clonedObject = super.clone();
        final PluginGroup clonedGroup = (PluginGroup)clonedObject;
        clonedGroup.groupLabel = new byte[4];
        System.arraycopy(this.groupLabel, 0, clonedGroup.groupLabel, 0, 4);
        clonedGroup.timestamp = new byte[4];
        System.arraycopy(this.timestamp, 0, clonedGroup.timestamp, 0, 4);
        clonedGroup.recordList = new ArrayList<SerializedElement>(this.recordList.size());
        for (final SerializedElement element : this.recordList) {
            final SerializedElement clonedElement = (SerializedElement)element.clone();
            clonedElement.setParent(clonedGroup);
            clonedGroup.recordList.add(clonedElement);
        }
        return clonedObject;
    }
    
    static {
        PluginGroup.groupDescriptions = new String[][] { { "ACTI", "Activators" }, { "ADDN", "Addon Node" }, { "ALCH", "Ingestibles" }, { "ALOC", "Media Location Controller" }, { "AMEF", "Ammo Effect" }, { "AMMO", "Ammunition" }, { "ANIO", "Animated Object" }, { "ARMA", "Armor Addon" }, { "ARMO", "Armor" }, { "ASPC", "Acoustic Spaces" }, { "AVIF", "Actor Value Information" }, { "BOOK", "Books" }, { "BPTD", "Body Part Data" }, { "CAMS", "Camera Shots" }, { "CCRD", "Caravan Card" }, { "CDCK", "Caravan Deck" }, { "CELL", "Cells" }, { "CHAL", "Challenge" }, { "CHIP", "Casino Chip" }, { "CLAS", "Classes" }, { "CLMT", "Climates" }, { "CMNY", "Casino Money" }, { "COBJ", "Constructible Objects" }, { "CONT", "Containers" }, { "CPTH", "Camera Paths" }, { "CREA", "Creatures" }, { "CSNO", "Casino" }, { "CSTY", "Combat Styles" }, { "DEBR", "Debris" }, { "DEHY", "Dehydration Stage" }, { "DIAL", "Dialog Topics" }, { "DOBJ", "Default Object Managers" }, { "DOOR", "Doors" }, { "ECZN", "Encounter Zones" }, { "EFSH", "Effect Shaders" }, { "ENCH", "Object Effects" }, { "EXPL", "Explosions" }, { "EYES", "Eyes" }, { "FACT", "Factions" }, { "FLST", "Form Lists" }, { "FURN", "Furniture" }, { "GLOB", "Globals" }, { "GMST", "Game Settings" }, { "GRAS", "Grass" }, { "HAIR", "Hair" }, { "HDPT", "Head Parts" }, { "HUNG", "Hunger Stage" }, { "IDLE", "Idle Animations" }, { "IDLM", "Idle Markers" }, { "IMAD", "Image Space Modifiers" }, { "IMGS", "Image Spaces" }, { "IMOD", "Item Mod" }, { "INGR", "Ingredients" }, { "IPCT", "Impact Data" }, { "IPDS", "Impact Data Sets" }, { "KEYM", "Keys" }, { "LGTM", "Lighting Templates" }, { "LIGH", "Lights" }, { "LSCR", "Load Screens" }, { "LSCT", "Load Screen Type" }, { "LTEX", "Land Textures" }, { "LVLC", "Leveled Creatures" }, { "LVLI", "Leveled Items" }, { "LVLN", "Leveled Characters" }, { "MESG", "Messages" }, { "MGEF", "Base Effects" }, { "MICN", "Menu Icons" }, { "MISC", "Miscellaneous Items" }, { "MSET", "Media Set" }, { "MSTT", "Moveable Statics" }, { "MUSC", "Music Types" }, { "NAVI", "Navigation Mesh Information" }, { "NOTE", "Notes" }, { "NPC_", "NPCs" }, { "PACK", "Packages" }, { "PERK", "Perks" }, { "PROJ", "Projectiles" }, { "PWAT", "Placeable Water" }, { "QUST", "Quests" }, { "RACE", "Races" }, { "RADS", "Radiation Stages" }, { "RCCT", "Recipe Category" }, { "RCPE", "Recipe" }, { "REGN", "Regions" }, { "REPU", "Reputation" }, { "RGDL", "Ragdolls" }, { "SCOL", "Static Collections" }, { "SCPT", "Scripts" }, { "SLPD", "Sleep Deprivation Stage" }, { "SOUN", "Sounds" }, { "SPEL", "Actor Effects" }, { "STAT", "Statics" }, { "TACT", "Talking Activators" }, { "TERM", "Terminals" }, { "TREE", "Trees" }, { "TXST", "Texture Sets" }, { "VTYP", "Voice Types" }, { "WATR", "Water" }, { "WEAP", "Weapons" }, { "WRLD", "World Spaces" }, { "WTHR", "Weather" } };
    }
}
