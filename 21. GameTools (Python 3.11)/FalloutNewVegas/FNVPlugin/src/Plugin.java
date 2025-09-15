// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import java.io.FileOutputStream;
import java.io.FileInputStream;
import java.util.zip.DataFormatException;
import java.io.RandomAccessFile;
import java.io.IOException;
import java.util.ListIterator;
import java.util.Iterator;
import java.util.HashMap;
import java.util.ArrayList;
import java.util.Map;
import java.util.List;
import java.io.File;

public class Plugin extends SerializedElement
{
    private static final String[] initialGroupList;
    private File pluginFile;
    private float pluginVersion;
    private int formVersion;
    private int nextFormID;
    private boolean master;
    private String creator;
    private String summary;
    private List<MasterEntry> masterList;
    private List<PluginGroup> groupList;
    private List<PluginRecord> recordList;
    private Map<Integer, PluginRecord> formIDMap;
    
    public Plugin(final File pluginFile) {
        this.pluginFile = pluginFile;
        this.pluginVersion = 1.32f;
        this.formVersion = 15;
        this.nextFormID = 3750;
        this.creator = "DEFAULT";
        this.summary = "";
        this.masterList = new ArrayList<MasterEntry>(4);
        this.groupList = new ArrayList<PluginGroup>(128);
        this.recordList = new ArrayList<PluginRecord>(1024);
        this.formIDMap = new HashMap<Integer, PluginRecord>();
    }
    
    public Plugin(final File pluginFile, final String creator, final String summary, final List<MasterEntry> masterList) {
        this.pluginFile = pluginFile;
        this.creator = creator;
        this.summary = summary;
        this.masterList = masterList;
        this.pluginVersion = 1.32f;
        this.formVersion = 15;
        this.nextFormID = 3750;
        this.groupList = new ArrayList<PluginGroup>(128);
        this.recordList = new ArrayList<PluginRecord>(1024);
        this.formIDMap = new HashMap<Integer, PluginRecord>();
    }
    
    public File getFile() {
        return this.pluginFile;
    }
    
    public void setFile(final File pluginFile) {
        this.pluginFile = pluginFile;
    }
    
    public String getName() {
        return this.pluginFile.getName();
    }
    
    public float getPluginVersion() {
        return this.pluginVersion;
    }
    
    public void setPluginVersion(final float version) {
        this.pluginVersion = version;
    }
    
    public int getFormVersion() {
        return this.formVersion;
    }
    
    public void setFormVersion(final int version) {
        this.formVersion = version;
    }
    
    public int getNextFormID() {
        return this.nextFormID;
    }
    
    public void setNextFormID(final int formID) {
        this.nextFormID = formID;
    }
    
    public String getCreator() {
        return this.creator;
    }
    
    public void setCreator(final String creator) {
        this.creator = creator;
    }
    
    public String getSummary() {
        return this.summary;
    }
    
    public void setSummary(final String summary) {
        this.summary = summary;
    }
    
    public int getRecordCount() {
        int recordCount = 0;
        for (final PluginGroup group : this.groupList) {
            recordCount += group.getRecordCount() + 1;
        }
        return recordCount;
    }
    
    public boolean isMaster() {
        return this.master;
    }
    
    public void setMaster(final boolean master) {
        this.master = master;
    }
    
    public List<MasterEntry> getMasterList() {
        return this.masterList;
    }
    
    public List<PluginGroup> getGroupList() {
        return this.groupList;
    }
    
    public List<PluginRecord> getRecordList() {
        return this.recordList;
    }
    
    public Map<Integer, PluginRecord> getFormIDMap() {
        return this.formIDMap;
    }
    
    public PluginRecord getRecord(final int formID) {
        return this.formIDMap.get(new Integer(formID));
    }
    
    public PluginGroup createTopGroup(final String recordType) throws PluginException {
        PluginGroup group = null;
        boolean foundGroup = false;
        boolean createdGroup = false;
        for (final PluginGroup checkGroup : this.groupList) {
            if (checkGroup.getGroupRecordType().equals(recordType)) {
                group = checkGroup;
                break;
            }
        }
        if (group != null) {
            return group;
        }
        int index;
        for (index = 0; index < Plugin.initialGroupList.length; ++index) {
            if (Plugin.initialGroupList[index].equals(recordType)) {
                foundGroup = true;
                break;
            }
        }
        if (!foundGroup) {
            throw new PluginException("TOP group type " + recordType + " is not valid");
        }
        for (int size = this.groupList.size(), i = 0; i < size; ++i) {
            group = this.groupList.get(i);
            final String groupRecordType = group.getGroupRecordType();
            for (int j = 0; j < Plugin.initialGroupList.length; ++j) {
                if (Plugin.initialGroupList[j].equals(groupRecordType) && j > index) {
                    group = new PluginGroup(this, recordType);
                    this.groupList.add(i, group);
                    createdGroup = true;
                    break;
                }
            }
            if (createdGroup) {
                break;
            }
        }
        if (!createdGroup) {
            group = new PluginGroup(this, recordType);
            this.groupList.add(group);
        }
        return group;
    }
    
    public PluginGroup createHierarchy(final SerializedElement element, final FormAdjust formAdjust) throws PluginException {
        PluginGroup group = null;
        PluginRecord record = null;
        PluginGroup pluginGroup = null;
        if (element instanceof PluginGroup) {
            group = (PluginGroup)element;
        }
        else {
            record = (PluginRecord)element;
        }
        final PluginGroup parentGroup = (PluginGroup)element.getParent();
        if (parentGroup != null) {
            int groupType = parentGroup.getGroupType();
            if (groupType == 0) {
                pluginGroup = this.createTopGroup(parentGroup.getGroupRecordType());
            }
            else {
                boolean foundGroup = false;
                if (group != null) {
                    if (group.getGroupType() == 6) {
                        final int newFormID = formAdjust.adjustFormID(group.getGroupParentID());
                        final SerializedElement checkElement = this.formIDMap.get(new Integer(newFormID));
                        if (checkElement != null) {
                            pluginGroup = (PluginGroup)checkElement.getParent();
                            foundGroup = true;
                        }
                    }
                }
                else if (record.getRecordType().equals("CELL")) {
                    final int newFormID = formAdjust.adjustFormID(record.getFormID());
                    final SerializedElement checkElement = this.formIDMap.get(new Integer(newFormID));
                    if (checkElement != null) {
                        pluginGroup = (PluginGroup)checkElement.getParent();
                        foundGroup = true;
                    }
                }
                if (!foundGroup) {
                    final PluginGroup grandparentGroup = this.createHierarchy(parentGroup, formAdjust);
                    final byte[] groupLabel = parentGroup.getGroupLabel();
                    int groupParentID = 0;
                    switch (groupType) {
                        case 1:
                        case 6:
                        case 7:
                        case 8:
                        case 9:
                        case 10: {
                            groupParentID = formAdjust.adjustFormID(parentGroup.getGroupParentID());
                            break;
                        }
                    }
                    final List<SerializedElement> parentRecordList = grandparentGroup.getRecordList();
                    for (final SerializedElement parentRecord : parentRecordList) {
                        if (parentRecord instanceof PluginGroup) {
                            pluginGroup = (PluginGroup)parentRecord;
                            final int checkType = pluginGroup.getGroupType();
                            if (checkType != groupType) {
                                continue;
                            }
                            if (groupParentID != 0) {
                                if (pluginGroup.getGroupParentID() == groupParentID) {
                                    foundGroup = true;
                                    break;
                                }
                                continue;
                            }
                            else {
                                if (SerializedElement.compareArrays(pluginGroup.getGroupLabel(), 0, groupLabel, 0, 4) == 0) {
                                    foundGroup = true;
                                    break;
                                }
                                continue;
                            }
                        }
                    }
                    if (!foundGroup) {
                        if (groupParentID != 0) {
                            pluginGroup = new PluginGroup(grandparentGroup, groupType, groupParentID);
                        }
                        else {
                            pluginGroup = new PluginGroup(grandparentGroup, groupType, groupLabel);
                        }
                        if (groupType == 10 || groupType == 8) {
                            parentRecordList.add(0, pluginGroup);
                        }
                        else {
                            parentRecordList.add(pluginGroup);
                        }
                        if (Main.debugMode) {
                            System.out.printf("%s: Created parent group %s\n", this.pluginFile.getName(), pluginGroup.toString());
                        }
                    }
                }
            }
            if (group != null) {
                groupType = group.getGroupType();
                if (groupType == 1 || groupType == 6 || groupType == 7) {
                    final int groupParentID2 = formAdjust.adjustFormID(group.getGroupParentID());
                    final List<SerializedElement> parentRecordList2 = parentGroup.getRecordList();
                    final int parentRecordCount = parentRecordList2.size();
                    int index = 1;
                    while (index < parentRecordCount) {
                        if (parentRecordList2.get(index) == group) {
                            final SerializedElement prevElement = parentRecordList2.get(index - 1);
                            if (prevElement instanceof PluginRecord) {
                                final PluginRecord prevRecord = (PluginRecord)prevElement;
                                final String recordType = prevRecord.getRecordType();
                                if (recordType.equals("WRLD") || recordType.equals("CELL") || recordType.equals("DIAL")) {
                                    final int formID = prevRecord.getFormID();
                                    if (group.getGroupParentID() == formID && this.formIDMap.get(new Integer(groupParentID2)) == null) {
                                        this.copyRecord(prevRecord, formAdjust);
                                    }
                                }
                                break;
                            }
                            break;
                        }
                        else {
                            ++index;
                        }
                    }
                }
            }
            return pluginGroup;
        }
        if (group != null) {
            throw new PluginException(String.format("Type %d group does not have a parent", group.getGroupType()));
        }
        throw new PluginException(String.format("%s record %s (%08X) does not have a parent", record.getRecordType(), record.getEditorID(), record.getFormID()));
    }
    
    public void copyRecord(final PluginRecord record, final FormAdjust formAdjust) throws PluginException {
        final PluginGroup pluginGroup = this.createHierarchy(record, formAdjust);
        final List<SerializedElement> groupRecordList = pluginGroup.getRecordList();
        final int formID = formAdjust.adjustFormID(record.getFormID());
        final Integer mapFormID = new Integer(formID);
        String editorID = formAdjust.adjustEditorID(record.getFormID());
        if (editorID == null) {
            editorID = record.getEditorID();
        }
        final String recordType = record.getRecordType();
        final PluginRecord pluginRecord = (PluginRecord)record.clone();
        pluginRecord.setFormID(formID);
        pluginRecord.setEditorID(editorID);
        pluginRecord.setParent(pluginGroup);
        pluginRecord.updateReferences(formAdjust);
        groupRecordList.add(pluginRecord);
        this.recordList.add(pluginRecord);
        this.formIDMap.put(mapFormID, pluginRecord);
        if (Main.debugMode) {
            System.out.printf("%s: Added %s record %s (%08X)\n", this.pluginFile.getName(), recordType, editorID, formID);
        }
        if (!pluginRecord.isDeleted()) {
            PluginGroup subgroup = null;
            if (recordType.equals("WRLD")) {
                subgroup = new PluginGroup(pluginGroup, 1, formID);
            }
            else if (recordType.equals("CELL")) {
                subgroup = new PluginGroup(pluginGroup, 6, formID);
            }
            else if (recordType.equals("DIAL")) {
                subgroup = new PluginGroup(pluginGroup, 7, formID);
            }
            if (subgroup != null) {
                groupRecordList.add(subgroup);
                if (Main.debugMode) {
                    System.out.printf("%s: Added type %d group %08X\n", this.pluginFile.getName(), subgroup.getGroupType(), formID);
                }
            }
        }
    }
    
    public void removeGroupRecords(final PluginGroup group) {
        final List<SerializedElement> recordList = group.getRecordList();
        for (final SerializedElement element : recordList) {
            if (element instanceof PluginGroup) {
                this.removeGroupRecords((PluginGroup)element);
            }
            else {
                final PluginRecord record = (PluginRecord)element;
                recordList.remove(record);
                this.formIDMap.remove(new Integer(record.getFormID()));
            }
        }
    }
    
    public void removeRecord(final PluginRecord record) {
        final int formID = record.getFormID();
        final String recordType = record.getRecordType();
        final PluginGroup parentGroup = (PluginGroup)record.getParent();
        final List<SerializedElement> parentRecordList = parentGroup.getRecordList();
        final int index = parentRecordList.indexOf(record);
        if (index >= 0) {
            final Integer mapFormID = new Integer(formID);
            parentRecordList.remove(index);
            this.recordList.remove(record);
            this.formIDMap.remove(mapFormID);
            if ((recordType.equals("WRLD") || recordType.equals("CELL") || recordType.equals("DIAL")) && index < this.recordList.size()) {
                final SerializedElement checkElement = parentRecordList.get(index);
                if (checkElement instanceof PluginGroup) {
                    final PluginGroup subgroup = (PluginGroup)checkElement;
                    final int groupType = subgroup.getGroupType();
                    if ((groupType == 1 || groupType == 6 || groupType == 7) && subgroup.getGroupParentID() == formID) {
                        this.removeGroupRecords(subgroup);
                        parentRecordList.remove(index);
                    }
                }
            }
        }
    }
    
    public void buildFormOverrides() {
        final int masterCount = this.masterList.size();
        for (final MasterEntry masterEntry : this.masterList) {
            masterEntry.getOverrides().clear();
        }
        if (!this.isMaster()) {
            return;
        }
        for (final PluginRecord record : this.recordList) {
            final int formID = record.getFormID();
            final int masterIndex = formID >>> 24;
            if (masterIndex < masterCount) {
                final String recordType = record.getRecordType();
                if (!recordType.equals("LAND") && !recordType.equals("NAVM") && !recordType.equals("REFR") && !recordType.equals("PGRE") && !recordType.equals("PMIS") && !recordType.equals("ACRE") && !recordType.equals("ACHR")) {
                    continue;
                }
                final MasterEntry masterEntry2 = this.masterList.get(masterIndex);
                masterEntry2.getOverrides().add(new Integer(formID & 0xFFFFFF));
            }
        }
    }
    
    public void purgeNavInfo() {
        PluginRecord navInfoRecord = null;
        for (final PluginGroup group : this.groupList) {
            if (group.getGroupRecordType().equals("NAVI")) {
                final List<SerializedElement> elementList = group.getRecordList();
                if (elementList.size() > 0) {
                    final SerializedElement element = elementList.get(0);
                    if (element instanceof PluginRecord && ((PluginRecord)element).getRecordType().equals("NAVI")) {
                        navInfoRecord = (PluginRecord)element;
                    }
                    break;
                }
                break;
            }
        }
        if (navInfoRecord == null) {
            return;
        }
        final List<PluginSubrecord> subrecordList = navInfoRecord.getSubrecords();
        final ListIterator<PluginSubrecord> lit = subrecordList.listIterator();
        while (lit.hasNext()) {
            final PluginSubrecord subrecord = lit.next();
            final String subrecordType = subrecord.getSubrecordType();
            final byte[] subrecordData = subrecord.getSubrecordData();
            if (subrecordType.equals("NVMI")) {
                if (subrecordData.length < 8) {
                    continue;
                }
                final int formID = SerializedElement.getInteger(subrecordData, 4);
                if (this.formIDMap.get(new Integer(formID)) != null) {
                    continue;
                }
                lit.remove();
            }
            else {
                if (!subrecordType.equals("NVCI") || subrecordData.length < 4) {
                    continue;
                }
                final int formID = SerializedElement.getInteger(subrecordData, 0);
                if (this.formIDMap.get(new Integer(formID)) != null) {
                    continue;
                }
                lit.remove();
            }
        }
    }
    
    public void load(final WorkerTask task) throws PluginException, DataFormatException, IOException, InterruptedException {
        RandomAccessFile in = null;
        StatusDialog statusDialog = null;
        if (task != null) {
            statusDialog = task.getStatusDialog();
            if (statusDialog != null) {
                statusDialog.updateMessage("Loading " + this.pluginFile.getName());
            }
        }
        try {
            final byte[] prefix = new byte[24];
            byte[] buffer = new byte[1024];
            int recordCount = 0;
            int loadCount = 0;
            MasterEntry masterEntry = null;
            if (!this.pluginFile.exists() || !this.pluginFile.isFile()) {
                throw new IOException("Plugin file '" + this.pluginFile.getName() + "' does not exist");
            }
            in = new RandomAccessFile(this.pluginFile, "r");
            int count = in.read(prefix);
            if (count != 24) {
                throw new PluginException(this.pluginFile.getName() + ": File is not a Fallout 3 file");
            }
            String type = new String(prefix, 0, 4);
            if (!type.equals("TES4")) {
                throw new PluginException(this.pluginFile.getName() + ": File is not a Fallout 3 file");
            }
            if ((prefix[8] & 0x1) != 0x0) {
                this.master = true;
            }
            else {
                this.master = false;
            }
            this.formVersion = SerializedElement.getInteger(prefix, 20);
            int headerLength = SerializedElement.getInteger(prefix, 4);
            while (headerLength >= 6) {
                count = in.read(prefix, 0, 6);
                if (count != 6) {
                    throw new PluginException(this.pluginFile.getName() + ": Header subrecord prefix truncated");
                }
                headerLength -= 6;
                final int length = SerializedElement.getShort(prefix, 4);
                if (length > headerLength) {
                    throw new PluginException(this.pluginFile.getName() + ": Subrecord length exceeds header length");
                }
                if (length > buffer.length) {
                    buffer = new byte[length];
                }
                count = in.read(buffer, 0, length);
                if (count != length) {
                    throw new PluginException(this.pluginFile.getName() + ": Header subrecord data truncated");
                }
                headerLength -= count;
                type = new String(prefix, 0, 4);
                if (type.equals("HEDR")) {
                    if (length < 12) {
                        throw new PluginException(this.pluginFile.getName() + ": HEDR subrecord is too small");
                    }
                    final int pluginIntVersion = SerializedElement.getInteger(buffer, 0);
                    this.pluginVersion = Float.intBitsToFloat(pluginIntVersion);
                    if (Main.debugMode) {
                        System.out.printf("%s: Version %f\n", this.pluginFile.getName(), this.pluginVersion);
                    }
                    recordCount = SerializedElement.getInteger(buffer, 4);
                    if (Main.debugMode) {
                        System.out.printf("%s: %d records\n", this.pluginFile.getName(), recordCount);
                    }
                    this.nextFormID = SerializedElement.getInteger(buffer, 8);
                    if (Main.debugMode) {
                        System.out.printf("%s: Next form ID is %08X\n", this.pluginFile.getName(), this.nextFormID);
                    }
                    if (this.pluginVersion != 1.32f && this.pluginVersion != 1.33f && this.pluginVersion != 1.34f) {
                        throw new PluginException(this.pluginFile.getName() + ": Plugin version " + this.pluginVersion + " is not supported");
                    }
                    continue;
                }
                else if (type.equals("CNAM")) {
                    if (length <= 1) {
                        continue;
                    }
                    this.creator = new String(buffer, 0, length - 1);
                }
                else if (type.equals("SNAM")) {
                    if (length <= 1) {
                        continue;
                    }
                    this.summary = new String(buffer, 0, length - 1);
                }
                else if (type.equals("MAST")) {
                    if (length <= 1) {
                        continue;
                    }
                    masterEntry = new MasterEntry(new String(buffer, 0, length - 1));
                    this.masterList.add(masterEntry);
                }
                else {
                    if (type.equals("DATA")) {
                        continue;
                    }
                    if (!type.equals("ONAM")) {
                        throw new PluginException(this.pluginFile.getName() + ": Unrecognized " + type + " header subrecord");
                    }
                    if (masterEntry == null) {
                        throw new PluginException(this.pluginFile.getName() + ": Unexpected ONAM header subrecord");
                    }
                    final List<Integer> masterOverrides = masterEntry.getOverrides();
                    for (int offset = 0; offset <= length - 4; offset += 4) {
                        masterOverrides.add(new Integer(SerializedElement.getInteger(buffer, offset)));
                    }
                    masterEntry = null;
                }
            }
            if (headerLength != 0) {
                throw new PluginException(this.pluginFile.getName() + ": Header is incomplete");
            }
            this.recordList = new ArrayList<PluginRecord>(recordCount);
            this.formIDMap = new HashMap<Integer, PluginRecord>(recordCount);
            while (true) {
                count = in.read(prefix);
                if (count == -1) {
                    if (loadCount != recordCount) {
                        final String text = this.pluginFile.getName() + ": Load count " + loadCount + " does not match header count " + recordCount;
                        final int selection = WorkerDialog.showConfirmDialog(task.getParent(), text + ". Do you want to continue?", "Error", 0, 0, false);
                        if (selection != 0) {
                            throw new PluginException(text);
                        }
                    }
                    break;
                }
                if (count != 24) {
                    throw new PluginException(this.pluginFile.getName() + ": Group record prefix is too short");
                }
                type = new String(prefix, 0, 4);
                if (!type.equals("GRUP")) {
                    throw new PluginException(this.pluginFile.getName() + ": Top-level record is not a group");
                }
                if (prefix[12] != 0) {
                    throw new PluginException(this.pluginFile.getName() + ": Top-level group type is not 0");
                }
                final int length = SerializedElement.getInteger(prefix, 4);
                if (Main.debugMode) {
                    System.out.printf("%s: Loading group %s\n", this.pluginFile.getName(), new String(prefix, 8, 4));
                }
                final PluginGroup group = new PluginGroup(this, this.pluginFile, in, prefix);
                this.groupList.add(group);
                loadCount += group.updateMappings(this.recordList, this.formIDMap) + 1;
                if (task != null && Thread.interrupted()) {
                    throw new InterruptedException("Request canceled");
                }
            }
        }
        finally {
            if (in != null) {
                in.close();
            }
        }
    }
    
    public void store(final WorkerTask task) throws DataFormatException, IOException, InterruptedException, PluginException {
        File outFile = null;
        RandomAccessFile out = null;
        StatusDialog statusDialog = null;
        boolean groupsWritten = false;
        if (task != null) {
            statusDialog = task.getStatusDialog();
            if (statusDialog != null) {
                statusDialog.updateMessage("Saving " + this.pluginFile.getName());
            }
        }
        try {
            int recordCount = 0;
            final ListIterator<PluginGroup> lit = this.groupList.listIterator();
            while (lit.hasNext()) {
                final PluginGroup group = lit.next();
                group.removeIgnoredRecords(this.recordList, this.formIDMap);
                final int count = group.getRecordCount();
                if (count != 0) {
                    recordCount += count + 1;
                }
                else {
                    lit.remove();
                }
            }
            this.purgeNavInfo();
            outFile = new File(this.pluginFile.getParent() + Main.fileSeparator + "FO3Plugin.tmp");
            if (outFile.exists() && !outFile.delete()) {
                throw new IOException("Unable to delete '" + outFile.getPath() + "'");
            }
            out = new RandomAccessFile(outFile, "rw");
            final int pluginIntVersion = Float.floatToIntBits(this.pluginVersion);
            final byte[] hedrSubrecord = new byte[18];
            System.arraycopy("HEDR".getBytes(), 0, hedrSubrecord, 0, 4);
            SerializedElement.setShort(12, hedrSubrecord, 4);
            SerializedElement.setInteger(pluginIntVersion, hedrSubrecord, 6);
            SerializedElement.setInteger(recordCount, hedrSubrecord, 10);
            SerializedElement.setInteger(this.nextFormID, hedrSubrecord, 14);
            final byte[] creatorBytes = this.creator.getBytes();
            int length = creatorBytes.length + 1;
            final byte[] cnamSubrecord = new byte[6 + length];
            System.arraycopy("CNAM".getBytes(), 0, cnamSubrecord, 0, 4);
            SerializedElement.setShort(length, cnamSubrecord, 4);
            if (length > 1) {
                System.arraycopy(creatorBytes, 0, cnamSubrecord, 6, creatorBytes.length);
            }
            cnamSubrecord[6 + creatorBytes.length] = 0;
            final byte[] summaryBytes = this.summary.getBytes();
            length = summaryBytes.length + 1;
            byte[] snamSubrecord;
            if (length > 1) {
                snamSubrecord = new byte[6 + length];
                System.arraycopy("SNAM".getBytes(), 0, snamSubrecord, 0, 4);
                SerializedElement.setShort(length, snamSubrecord, 4);
                System.arraycopy(summaryBytes, 0, snamSubrecord, 6, summaryBytes.length);
                snamSubrecord[6 + summaryBytes.length] = 0;
            }
            else {
                snamSubrecord = new byte[0];
            }
            final byte[][] masterSubrecords = new byte[this.masterList.size()][];
            int count = 0;
            for (final MasterEntry master : this.masterList) {
                final String masterName = master.getName();
                final List<Integer> masterOverrides = master.getOverrides();
                final byte[] masterBytes = masterName.getBytes();
                final int nameLength = masterBytes.length + 1;
                final int overrideLength = masterOverrides.size() * 4;
                if (overrideLength > 16383) {
                    throw new PluginException(this.pluginFile.getName() + ": Too many master override records");
                }
                length = 6 + nameLength + 6 + 8;
                if (overrideLength > 0) {
                    length += 6 + overrideLength;
                }
                final byte[] masterSubrecord = new byte[length];
                int offset = 0;
                System.arraycopy("MAST".getBytes(), 0, masterSubrecord, offset, 4);
                SerializedElement.setShort(nameLength, masterSubrecord, offset + 4);
                if (nameLength > 1) {
                    System.arraycopy(masterBytes, 0, masterSubrecord, offset + 6, masterBytes.length);
                }
                masterSubrecord[offset + 6 + masterBytes.length] = 0;
                offset += 6 + nameLength;
                System.arraycopy("DATA".getBytes(), 0, masterSubrecord, offset, 4);
                SerializedElement.setShort(8, masterSubrecord, offset + 4);
                offset += 14;
                if (overrideLength != 0) {
                    System.arraycopy("ONAM".getBytes(), 0, masterSubrecord, offset, 4);
                    SerializedElement.setShort(overrideLength, masterSubrecord, offset + 4);
                    offset += 6;
                    for (final Integer override : masterOverrides) {
                        SerializedElement.setInteger(override, masterSubrecord, offset);
                        offset += 4;
                    }
                }
                masterSubrecords[count++] = masterSubrecord;
            }
            length = hedrSubrecord.length + cnamSubrecord.length + snamSubrecord.length;
            for (int i = 0; i < masterSubrecords.length; ++i) {
                length += masterSubrecords[i].length;
            }
            final byte[] headerRecord = new byte[24 + length];
            System.arraycopy("TES4".getBytes(), 0, headerRecord, 0, 4);
            SerializedElement.setInteger(length, headerRecord, 4);
            headerRecord[8] = (byte)(this.master ? 1 : 0);
            SerializedElement.setInteger(this.formVersion, headerRecord, 20);
            int offset = 24;
            System.arraycopy(hedrSubrecord, 0, headerRecord, offset, hedrSubrecord.length);
            offset += hedrSubrecord.length;
            System.arraycopy(cnamSubrecord, 0, headerRecord, offset, cnamSubrecord.length);
            offset += cnamSubrecord.length;
            if (snamSubrecord.length != 0) {
                System.arraycopy(snamSubrecord, 0, headerRecord, offset, snamSubrecord.length);
                offset += snamSubrecord.length;
            }
            for (int j = 0; j < masterSubrecords.length; ++j) {
                System.arraycopy(masterSubrecords[j], 0, headerRecord, offset, masterSubrecords[j].length);
                offset += masterSubrecords[j].length;
            }
            out.write(headerRecord);
            for (final PluginGroup group2 : this.groupList) {
                group2.store(out);
                if (task != null && Thread.interrupted()) {
                    throw new InterruptedException("Request canceled");
                }
            }
            groupsWritten = true;
        }
        finally {
            if (out != null) {
                out.close();
            }
            if (outFile != null && outFile.exists()) {
                if (groupsWritten) {
                    if (this.pluginFile.exists() && !this.pluginFile.delete()) {
                        throw new IOException("Unable to delete '" + this.pluginFile.getPath() + "'");
                    }
                    if (!outFile.renameTo(this.pluginFile)) {
                        throw new IOException("Unable to rename '" + outFile.getPath() + "'");
                    }
                }
                else if (!outFile.delete()) {
                    throw new IOException("Unable to delete '" + outFile.getPath() + "'");
                }
            }
        }
    }
    
    public void copyVoiceFiles(final String sourceName) throws IOException {
        final String voicePath = String.format("%s%sSound%sVoice", Main.pluginPath, Main.fileSeparator, Main.fileSeparator);
        final String targetPath = String.format("%s%s%s", voicePath, Main.fileSeparator, this.pluginFile.getName());
        final File targetDir = new File(targetPath);
        final String sourcePath = String.format("%s%s%s", voicePath, Main.fileSeparator, sourceName);
        final File sourceDir = new File(sourcePath);
        this.deleteVoiceFiles();
        if (!sourceDir.exists()) {
            return;
        }
        if (!sourceDir.isDirectory()) {
            throw new IOException("'" + sourceDir.getPath() + "' is not a directory");
        }
        if (!targetDir.mkdirs()) {
            throw new IOException("Unable to create directory '" + targetDir.getPath() + "'");
        }
        final File[] sourceFiles = sourceDir.listFiles();
        if (sourceFiles != null && sourceFiles.length != 0) {
            for (final File sourceFile : sourceFiles) {
                if (sourceFile.isDirectory()) {
                    this.copyVoiceSubdirectory(sourceFile, targetPath);
                }
            }
        }
    }
    
    private void copyVoiceSubdirectory(final File sourceDir, final String parentPath) throws IOException {
        final String targetPath = String.format("%s%s%s", parentPath, Main.fileSeparator, sourceDir.getName());
        final File targetDir = new File(targetPath);
        final File[] sourceFiles = sourceDir.listFiles();
        if (sourceFiles == null || sourceFiles.length == 0) {
            return;
        }
        if (!targetDir.exists() && !targetDir.mkdirs()) {
            throw new IOException("Unable to create directory '" + targetDir.getPath() + "'");
        }
        if (!targetDir.isDirectory()) {
            throw new IOException("'" + targetDir.getPath() + "' is not a directory");
        }
        final byte[] buffer = new byte[16384];
        for (final File sourceFile : sourceFiles) {
            FileInputStream in = null;
            FileOutputStream out = null;
            final File targetFile = new File(targetPath + Main.fileSeparator + sourceFile.getName());
            if (targetFile.exists() && !targetFile.delete()) {
                throw new IOException("Unable to delete '" + targetFile.getPath() + "'");
            }
            try {
                in = new FileInputStream(sourceFile);
                out = new FileOutputStream(targetFile);
                int count;
                while ((count = in.read(buffer)) >= 0) {
                    if (count > 0) {
                        out.write(buffer, 0, count);
                    }
                }
                out.close();
                out = null;
            }
            finally {
                if (in != null) {
                    in.close();
                }
                if (out != null) {
                    out.close();
                    if (targetFile.exists()) {
                        targetFile.delete();
                    }
                }
            }
        }
    }
    
    public void mergeVoiceFiles(final Plugin sourcePlugin, final Map<Integer, FormInfo> formInfoMap) throws IOException, PluginException {
        final String voicePath = String.format("%s%sSound%sVoice", Main.pluginPath, Main.fileSeparator, Main.fileSeparator);
        final String targetPath = String.format("%s%s%s", voicePath, Main.fileSeparator, this.pluginFile.getName());
        final File targetDir = new File(targetPath);
        final String sourcePath = String.format("%s%s%s", voicePath, Main.fileSeparator, sourcePlugin.getName());
        final File sourceDir = new File(sourcePath);
        if (!sourceDir.exists()) {
            return;
        }
        if (!sourceDir.isDirectory()) {
            throw new IOException("'" + sourceDir.getPath() + "' is not a directory");
        }
        if (targetDir.exists() && targetDir.isFile() && !targetDir.delete()) {
            throw new IOException("Unable to delete '" + targetDir.getPath() + "'");
        }
        if (!targetDir.exists() && !targetDir.mkdirs()) {
            throw new IOException("Unable to create directory '" + targetDir.getPath() + "'");
        }
        final File[] sourceFiles = sourceDir.listFiles();
        if (sourceFiles != null && sourceFiles.length != 0) {
            for (final File sourceFile : sourceFiles) {
                if (sourceFile.isDirectory()) {
                    this.mergeVoiceSubdirectory(sourceFile, targetPath, sourcePlugin, formInfoMap);
                }
            }
        }
    }
    
    private void mergeVoiceSubdirectory(final File sourceDir, final String parentPath, final Plugin sourcePlugin, final Map<Integer, FormInfo> formInfoMap) throws IOException, PluginException {
        final String targetPath = String.format("%s%s%s", parentPath, Main.fileSeparator, sourceDir.getName());
        final File targetDir = new File(targetPath);
        final File[] sourceFiles = sourceDir.listFiles();
        final int sourceMasterCount = sourcePlugin.getMasterList().size();
        if (sourceFiles == null || sourceFiles.length == 0) {
            return;
        }
        if (!targetDir.exists() && !targetDir.mkdirs()) {
            throw new IOException("Unable to create directory '" + targetDir.getPath() + "'");
        }
        if (!targetDir.isDirectory()) {
            throw new IOException("'" + targetDir.getPath() + "' is not a directory");
        }
        final byte[] buffer = new byte[16384];
        for (final File sourceFile : sourceFiles) {
            final String name = sourceFile.getName();
            int pos = 0;
            int sep = name.indexOf(95);
            if (sep <= pos) {
                throw new IOException("Malformed voice file name '" + name + "'");
            }
            String questName = name.substring(pos, sep);
            pos = sep + 1;
            sep = name.indexOf(95, pos);
            if (sep <= pos) {
                throw new IOException("Malformed voice file name '" + name + "'");
            }
            String topicName = name.substring(pos, sep);
            pos = sep + 1;
            sep = name.indexOf(95, pos);
            if (sep <= pos) {
                throw new IOException("Malformed voice file name '" + name + "'");
            }
            int infoID = 0;
            try {
                infoID = Integer.parseInt(name.substring(pos, sep), 16);
                infoID = ((infoID & 0xFFFFFF) | sourceMasterCount << 24);
            }
            catch (NumberFormatException exc) {
                throw new IOException("Malformed voice file name '" + name + "'");
            }
            final String nameSuffix = name.substring(sep);
            FormInfo formInfo = formInfoMap.get(new Integer(infoID));
            if (formInfo == null) {
                throw new PluginException(String.format("%s: Unable to locate INFO %08X for voice file %s", sourcePlugin.getName(), infoID, name));
            }
            final PluginRecord infoRecord = formInfo.getRecord();
            final int mergedInfoID = formInfo.getMergedFormID();
            final PluginGroup topicGroup = (PluginGroup)infoRecord.getParent();
            if (topicGroup == null || topicGroup.getGroupType() != 7) {
                throw new PluginException(String.format("%s: Topic group not found for INFO %08X", sourcePlugin.getName(), infoID));
            }
            final int topicID = topicGroup.getGroupParentID();
            int masterID = topicID >>> 24;
            if (masterID >= sourceMasterCount) {
                formInfo = formInfoMap.get(new Integer(topicID));
                if (formInfo == null) {
                    throw new PluginException(String.format("%s: Unable to locate DIAL %08X for INFO $08X", sourcePlugin.getName(), topicID, infoID));
                }
                topicName = formInfo.getMergedEditorID();
                if (topicName == null || topicName.length() == 0) {
                    throw new PluginException(String.format("%s: No merged editor ID for DIAL %08X", sourcePlugin.getName(), topicID));
                }
            }
            int questID = -1;
            final List<PluginSubrecord> subrecordList = infoRecord.getSubrecords();
            for (final PluginSubrecord subrecord : subrecordList) {
                if (subrecord.getSubrecordType().equals("QSTI")) {
                    final byte[] subrecordData = subrecord.getSubrecordData();
                    questID = SerializedElement.getInteger(subrecordData, 0);
                    break;
                }
            }
            if (questID == -1) {
                throw new PluginException(String.format("%s: No QSTI subrecord for INFO %08X", sourcePlugin.getName(), infoID));
            }
            masterID = questID >>> 24;
            if (masterID >= sourceMasterCount) {
                formInfo = formInfoMap.get(new Integer(questID));
                if (formInfo == null) {
                    throw new PluginException(String.format("%s: Unable to locate QUST %08X for Info %08X", sourcePlugin.getName(), questID, infoID));
                }
                questName = formInfo.getMergedEditorID();
                if (questName == null || questName.length() == 0) {
                    throw new PluginException(String.format("%s: No merged editor ID for QUST %08X", sourcePlugin.getName(), questID));
                }
            }
            if (questName.length() + topicName.length() > 25) {
                if (questName.length() > 10) {
                    questName = questName.substring(0, 10);
                }
                if (questName.length() + topicName.length() > 25) {
                    topicName = topicName.substring(0, 25 - questName.length());
                }
            }
            final String mergedName = String.format("%s_%s_%08X%s", questName, topicName, mergedInfoID & 0xFFFFFF, nameSuffix);
            FileInputStream in = null;
            FileOutputStream out = null;
            final File targetFile = new File(targetPath + Main.fileSeparator + mergedName);
            if (targetFile.exists() && !targetFile.delete()) {
                throw new IOException("Unable to delete '" + targetFile.getPath() + "'");
            }
            try {
                in = new FileInputStream(sourceFile);
                out = new FileOutputStream(targetFile);
                int count;
                while ((count = in.read(buffer)) >= 0) {
                    if (count > 0) {
                        out.write(buffer, 0, count);
                    }
                }
                out.close();
                out = null;
            }
            finally {
                if (in != null) {
                    in.close();
                }
                if (out != null) {
                    out.close();
                    if (targetFile.exists()) {
                        targetFile.delete();
                    }
                }
            }
        }
    }
    
    public void deleteVoiceFiles() throws IOException {
        final String voicePath = String.format("%s%sSound%sVoice", Main.pluginPath, Main.fileSeparator, Main.fileSeparator);
        final String targetPath = String.format("%s%s%s", voicePath, Main.fileSeparator, this.pluginFile.getName());
        final File targetDir = new File(targetPath);
        if (targetDir.exists()) {
            if (targetDir.isDirectory()) {
                this.deleteDirectory(targetDir);
            }
            else if (!targetDir.delete()) {
                throw new IOException("Unable to delete '" + targetDir.getPath() + "'");
            }
        }
    }
    
    private void deleteDirectory(final File dirFile) throws IOException {
        final File[] files = dirFile.listFiles();
        if (files != null && files.length != 0) {
            for (final File file : files) {
                if (file.isDirectory()) {
                    this.deleteDirectory(file);
                }
                else if (!file.delete()) {
                    throw new IOException("Unable to delete '" + file.getPath() + "'");
                }
            }
        }
        if (!dirFile.delete()) {
            throw new IOException("Unable to delete '" + dirFile.getPath() + "'");
        }
    }
    
    @Override
    public String toString() {
        return this.pluginFile.getName();
    }
    
    @Override
    public Object clone() {
        final Object clonedObject = super.clone();
        final Plugin clonedPlugin = (Plugin)clonedObject;
        clonedPlugin.pluginFile = new File(this.pluginFile.getPath());
        clonedPlugin.masterList = new ArrayList<MasterEntry>(this.masterList.size());
        clonedPlugin.groupList = new ArrayList<PluginGroup>(this.groupList.size());
        clonedPlugin.recordList = new ArrayList<PluginRecord>(this.recordList.size());
        clonedPlugin.formIDMap = new HashMap<Integer, PluginRecord>(this.recordList.size());
        for (final MasterEntry masterName : this.masterList) {
            clonedPlugin.masterList.add((MasterEntry)masterName.clone());
        }
        try {
            for (final PluginGroup group : this.groupList) {
                final PluginGroup clonedGroup = (PluginGroup)group.clone();
                clonedPlugin.groupList.add(clonedGroup);
                clonedGroup.updateMappings(clonedPlugin.recordList, clonedPlugin.formIDMap);
            }
        }
        catch (PluginException exc) {
            throw new UnsupportedOperationException("Unable to clone plugin", exc);
        }
        return clonedObject;
    }
    
    static {
        initialGroupList = new String[] { "GMST", "TXST", "MICN", "GLOB", "CLAS", "FACT", "HDPT", "HAIR", "EYES", "RACE", "SOUN", "ASPC", "MGEF", "SCPT", "LTEX", "ENCH", "SPEL", "ACTI", "TACT", "TERM", "ARMO", "BOOK", "CONT", "DOOR", "INGR", "LIGH", "MISC", "STAT", "SCOL", "MSTT", "PWAT", "GRAS", "TREE", "FURN", "WEAP", "AMMO", "NPC_", "CREA", "LVLC", "LVLN", "KEYM", "ALCH", "IDLM", "NOTE", "COBJ", "PROJ", "LVLI", "WTHR", "CLMT", "REGN", "NAVI", "CELL", "WRLD", "DIAL", "QUST", "IDLE", "PACK", "CSTY", "LSCR", "ANIO", "WATR", "EFSH", "EXPL", "DEBR", "IMGS", "IMAD", "FLST", "PERK", "BPTD", "ADDN", "AVIF", "RADS", "CAMS", "CPTH", "VTYP", "IPCT", "IPDS", "ARMA", "ECZN", "MESG", "RGDL", "DOBJ", "LGTM", "MUSC", "IMOD", "REPU", "RCPE", "RCCT", "CHIP", "CSNO", "LSCT", "MSET", "ALOC", "CHAL", "AMEF", "CCRD", "CMNY", "CDCK", "DEHY", "HUNG", "SLPD" };
    }
}
