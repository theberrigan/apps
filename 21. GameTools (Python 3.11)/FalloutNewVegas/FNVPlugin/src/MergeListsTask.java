// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import java.util.Map;
import java.util.Iterator;
import java.util.List;
import java.util.HashMap;
import java.util.ArrayList;
import java.io.IOException;
import java.util.zip.DataFormatException;
import javax.swing.JOptionPane;
import javax.swing.JDialog;
import javax.swing.JFrame;
import java.awt.Component;
import java.io.File;

public class MergeListsTask extends WorkerTask
{
    private Plugin plugin;
    private File[] mergeFiles;
    private PluginNode mergedNode;
    
    public MergeListsTask(final StatusDialog statusDialog, final Plugin plugin, final File[] mergeFiles) {
        super(statusDialog);
        this.plugin = plugin;
        this.mergeFiles = mergeFiles;
    }
    
    public static PluginNode mergeLists(final Component parent, final Plugin plugin, final File[] mergeFiles) {
        StatusDialog statusDialog;
        if (parent instanceof JFrame) {
            statusDialog = new StatusDialog((JFrame)parent, "Cloning current plugin", "Merge Lists");
        }
        else {
            statusDialog = new StatusDialog((JDialog)parent, "Cloning current plugin", "Merge Lists");
        }
        final MergeListsTask worker = new MergeListsTask(statusDialog, plugin, mergeFiles);
        statusDialog.setWorker(worker);
        worker.start();
        statusDialog.showDialog();
        if (statusDialog.getStatus() != 1) {
            worker.mergedNode = null;
            JOptionPane.showMessageDialog(parent, "Unable to merge lists", "Merge Lists", 1);
        }
        return worker.mergedNode;
    }
    
    @Override
    public void run() {
        boolean completed = false;
        boolean modified = false;
        final StatusDialog statusDialog = this.getStatusDialog();
        try {
            statusDialog.updateMessage("Cloning " + this.plugin.getName());
            final Plugin currentPlugin = (Plugin)this.plugin.clone();
            if (interrupted()) {
                throw new InterruptedException("Request canceled");
            }
            for (final File mergeFile : this.mergeFiles) {
                if (this.processPlugin(currentPlugin, mergeFile)) {
                    modified = true;
                }
            }
            if (modified) {
                (this.mergedNode = new PluginNode(currentPlugin)).buildNodes(this);
            }
            completed = true;
        }
        catch (PluginException exc) {
            Main.logException("Plugin Error", exc);
        }
        catch (DataFormatException exc2) {
            Main.logException("Compression Error", exc2);
        }
        catch (IOException exc3) {
            Main.logException("I/O Error", exc3);
        }
        catch (OperationCanceledException exc5) {}
        catch (InterruptedException exc6) {
            WorkerDialog.showMessageDialog(this.getStatusDialog(), "Request canceled", "Interrupted", 0);
        }
        catch (Throwable exc4) {
            Main.logException("Exception while merging lists", exc4);
        }
        statusDialog.closeDialog(completed);
    }
    
    private boolean processPlugin(final Plugin currentPlugin, final File mergeFile) throws DataFormatException, InterruptedException, IOException, OperationCanceledException, PluginException {
        final StatusDialog statusDialog = this.getStatusDialog();
        final Plugin mergePlugin = new Plugin(mergeFile);
        mergePlugin.load(this);
        final List<MasterEntry> mergeMasterList = mergePlugin.getMasterList();
        final int mergeMasterCount = mergeMasterList.size();
        statusDialog.updateMessage("Merging lists from " + mergeFile.getName());
        boolean foundOverride = false;
        final List<PluginGroup> groupList = mergePlugin.getGroupList();
        for (final PluginGroup group : groupList) {
            final String groupType = group.getGroupRecordType();
            if (groupType.equals("LVLC") || groupType.equals("LVLI") || groupType.equals("LVLN") || groupType.equals("CONT") || groupType.equals("FLST")) {
                final List<SerializedElement> elementList = group.getRecordList();
                for (final SerializedElement element : elementList) {
                    if (element instanceof PluginRecord) {
                        final int formID = ((PluginRecord)element).getFormID();
                        final int masterIndex = formID >>> 24;
                        if (masterIndex < mergeMasterCount) {
                            foundOverride = true;
                            break;
                        }
                        continue;
                    }
                }
            }
            if (foundOverride) {
                break;
            }
        }
        if (!foundOverride) {
            WorkerDialog.showMessageDialog(statusDialog, "No list override records in " + mergePlugin.getName(), "No Overrides", 1);
            return false;
        }
        final List<MasterEntry> masterList = currentPlugin.getMasterList();
        int masterCount = masterList.size();
        for (final MasterEntry masterEntry : masterList) {
            if (masterEntry.getName().equalsIgnoreCase(mergePlugin.getName())) {
                WorkerDialog.showMessageDialog(statusDialog, mergePlugin.getName() + " is in the master list for " + currentPlugin.getName(), "Dependent Plugin", 0);
                return false;
            }
        }
        for (final MasterEntry masterEntry : mergeMasterList) {
            final String masterName = masterEntry.getName();
            if (masterName.equalsIgnoreCase(currentPlugin.getName())) {
                WorkerDialog.showMessageDialog(statusDialog, currentPlugin.getName() + " is in the master list for " + mergePlugin.getName(), "Dependent Plugin", 0);
                return false;
            }
            boolean addMaster = true;
            for (final MasterEntry checkEntry : masterList) {
                if (checkEntry.getName().equalsIgnoreCase(masterName)) {
                    addMaster = false;
                    break;
                }
            }
            if (!addMaster) {
                continue;
            }
            masterList.add((MasterEntry)masterEntry.clone());
        }
        masterList.add(new MasterEntry(mergePlugin.getName()));
        final int[] masterAdjust = new int[masterCount];
        for (int i = 0; i < masterCount; ++i) {
            masterAdjust[i] = i;
        }
        masterCount = masterList.size();
        final int[] mergeMasterAdjust = new int[mergeMasterCount];
        for (int j = 0; j < mergeMasterCount; ++j) {
            final String masterName2 = mergeMasterList.get(j).getName();
            for (int k = 0; k < masterCount; ++k) {
                final String checkName = masterList.get(k).getName();
                if (checkName.equalsIgnoreCase(masterName2)) {
                    mergeMasterAdjust[j] = k;
                    break;
                }
            }
        }
        final FormAdjust formAdjust = new FormAdjust(masterAdjust, masterCount);
        final List<PluginRecord> recordList = currentPlugin.getRecordList();
        final Map<Integer, PluginRecord> formIDMap = currentPlugin.getFormIDMap();
        final int recordCount = recordList.size();
        formIDMap.clear();
        for (final PluginRecord record : recordList) {
            final int formID2 = record.getFormID();
            final int newFormID = formAdjust.adjustFormID(formID2);
            record.updateReferences(formAdjust);
            if (newFormID != formID2) {
                record.changeFormID(newFormID);
            }
            formIDMap.put(new Integer(newFormID), record);
        }
        if (interrupted()) {
            throw new InterruptedException("Request canceled");
        }
        final List<PluginRecord> mergeRecordList = mergePlugin.getRecordList();
        final int mergeRecordCount = mergeRecordList.size();
        final List<FormInfo> mergeFormInfoList = new ArrayList<FormInfo>(mergeRecordCount);
        final Map<Integer, FormInfo> mergeFormInfoMap = new HashMap<Integer, FormInfo>(mergeRecordCount);
        for (final PluginRecord mergeRecord : mergeRecordList) {
            if (mergeRecord.isIgnored()) {
                continue;
            }
            int formID3 = mergeRecord.getFormID();
            final FormInfo formInfo = new FormInfo(mergeRecord);
            mergeFormInfoList.add(formInfo);
            mergeFormInfoMap.put(new Integer(formID3), formInfo);
            final int mergeMasterIndex = formID3 >>> 24;
            if (mergeMasterIndex < mergeMasterCount) {
                continue;
            }
            formID3 = ((formID3 & 0xFFFFFF) | masterCount - 1 << 24);
            formInfo.setMergedFormID(formID3);
        }
        if (interrupted()) {
            throw new InterruptedException("Request canceled");
        }
        final FormAdjust mergeFormAdjust = new FormAdjust(mergeMasterAdjust, masterCount, mergeFormInfoMap);
        for (final FormInfo formInfo2 : mergeFormInfoList) {
            final PluginRecord mergeRecord2 = formInfo2.getRecord();
            int formID4 = mergeRecord2.getFormID();
            final String recordType = mergeRecord2.getRecordType();
            final int masterIndex2 = formID4 >>> 24;
            if (masterIndex2 >= mergeMasterCount) {
                continue;
            }
            formID4 = mergeFormAdjust.adjustFormID(formID4);
            final PluginRecord currentRecord = formIDMap.get(new Integer(formID4));
            if (recordType.equals("CONT")) {
                if (Main.debugMode) {
                    System.out.printf("%s: Processing CONT record %08X\n", mergePlugin.getName(), formInfo2.getFormID());
                }
                if (currentRecord == null) {
                    currentPlugin.copyRecord(mergeRecord2, mergeFormAdjust);
                }
                else {
                    final List<PluginSubrecord> currentSubrecordList = currentRecord.getSubrecords();
                    final List<PluginSubrecord> mergeSubrecordList = mergeRecord2.getSubrecords();
                    int startIndex = -1;
                    int listIndex = -1;
                    int addIndex = -1;
                    int dataIndex = -1;
                    for (final PluginSubrecord currentSubrecord : currentSubrecordList) {
                        ++listIndex;
                        final String subrecordType = currentSubrecord.getSubrecordType();
                        if (subrecordType.equals("CNTO")) {
                            addIndex = listIndex + 1;
                            if (startIndex != -1) {
                                continue;
                            }
                            startIndex = listIndex;
                        }
                        else {
                            if (!subrecordType.equals("DATA") || dataIndex != -1) {
                                continue;
                            }
                            dataIndex = listIndex;
                        }
                    }
                    if (addIndex == -1) {
                        if (dataIndex >= 0) {
                            addIndex = dataIndex;
                        }
                        else {
                            addIndex = listIndex + 1;
                        }
                    }
                    for (final PluginSubrecord mergeSubrecord : mergeSubrecordList) {
                        String subrecordType = mergeSubrecord.getSubrecordType();
                        if (subrecordType.equals("CNTO")) {
                            boolean addItem = true;
                            byte[] subrecordData = mergeSubrecord.getSubrecordData();
                            int itemID = SerializedElement.getInteger(subrecordData, 0);
                            itemID = mergeFormAdjust.adjustFormID(itemID);
                            if (startIndex >= 0) {
                                for (int l = startIndex; l < addIndex; ++l) {
                                    final PluginSubrecord checkSubrecord = currentSubrecordList.get(l);
                                    subrecordType = checkSubrecord.getSubrecordType();
                                    if (subrecordType.equals("CNTO")) {
                                        final byte[] checkData = checkSubrecord.getSubrecordData();
                                        final int checkID = SerializedElement.getInteger(checkData, 0);
                                        if (checkID == itemID) {
                                            addItem = false;
                                            break;
                                        }
                                    }
                                }
                            }
                            if (!addItem) {
                                continue;
                            }
                            final PluginSubrecord itemSubrecord = (PluginSubrecord)mergeSubrecord.clone();
                            subrecordData = itemSubrecord.getSubrecordData();
                            SerializedElement.setInteger(itemID, subrecordData, 0);
                            currentSubrecordList.add(addIndex, itemSubrecord);
                            if (startIndex == -1) {
                                startIndex = addIndex;
                            }
                            ++addIndex;
                        }
                    }
                }
            }
            else if (recordType.equals("FLST")) {
                if (Main.debugMode) {
                    System.out.printf("%s: Processing FLST record %08X\n", mergePlugin.getName(), formInfo2.getFormID());
                }
                if (currentRecord == null) {
                    currentPlugin.copyRecord(mergeRecord2, mergeFormAdjust);
                }
                else {
                    final List<PluginSubrecord> currentSubrecordList = currentRecord.getSubrecords();
                    final List<PluginSubrecord> mergeSubrecordList = mergeRecord2.getSubrecords();
                    int startIndex = -1;
                    int listIndex = -1;
                    int addIndex = -1;
                    for (final PluginSubrecord currentSubrecord2 : currentSubrecordList) {
                        ++listIndex;
                        final String subrecordType2 = currentSubrecord2.getSubrecordType();
                        if (subrecordType2.equals("LNAM")) {
                            addIndex = listIndex + 1;
                            if (startIndex != -1) {
                                continue;
                            }
                            startIndex = listIndex;
                        }
                    }
                    if (addIndex == -1) {
                        addIndex = listIndex + 1;
                    }
                    for (final PluginSubrecord mergeSubrecord2 : mergeSubrecordList) {
                        String subrecordType2 = mergeSubrecord2.getSubrecordType();
                        if (subrecordType2.equals("LNAM")) {
                            boolean addItem2 = true;
                            byte[] subrecordData2 = mergeSubrecord2.getSubrecordData();
                            int itemID2 = SerializedElement.getInteger(subrecordData2, 0);
                            itemID2 = mergeFormAdjust.adjustFormID(itemID2);
                            if (startIndex >= 0) {
                                for (int m = startIndex; m < addIndex; ++m) {
                                    final PluginSubrecord checkSubrecord2 = currentSubrecordList.get(m);
                                    subrecordType2 = checkSubrecord2.getSubrecordType();
                                    if (subrecordType2.equals("LNAM")) {
                                        final byte[] checkData2 = checkSubrecord2.getSubrecordData();
                                        final int checkID2 = SerializedElement.getInteger(checkData2, 0);
                                        if (checkID2 == itemID2) {
                                            addItem2 = false;
                                            break;
                                        }
                                    }
                                }
                            }
                            if (!addItem2) {
                                continue;
                            }
                            final PluginSubrecord itemSubrecord2 = (PluginSubrecord)mergeSubrecord2.clone();
                            subrecordData2 = itemSubrecord2.getSubrecordData();
                            SerializedElement.setInteger(itemID2, subrecordData2, 0);
                            currentSubrecordList.add(addIndex, itemSubrecord2);
                            if (startIndex == -1) {
                                startIndex = addIndex;
                            }
                            ++addIndex;
                        }
                    }
                }
            }
            else if (recordType.equals("LVLC") || recordType.equals("LVLI") || recordType.equals("LVLN")) {
                if (Main.debugMode) {
                    System.out.printf("%s: Processing %s record %08X\n", mergePlugin.getName(), recordType, formInfo2.getFormID());
                }
                if (currentRecord == null) {
                    currentPlugin.copyRecord(mergeRecord2, mergeFormAdjust);
                }
                else {
                    final List<PluginSubrecord> currentSubrecordList = currentRecord.getSubrecords();
                    final List<PluginSubrecord> mergeSubrecordList = mergeRecord2.getSubrecords();
                    int listIndex2 = -1;
                    int addIndex2 = -1;
                    int startIndex2 = -1;
                    for (final PluginSubrecord currentSubrecord2 : currentSubrecordList) {
                        ++listIndex2;
                        final String subrecordType2 = currentSubrecord2.getSubrecordType();
                        if (subrecordType2.equals("LVLO")) {
                            addIndex2 = listIndex2 + 1;
                            if (startIndex2 != -1) {
                                continue;
                            }
                            startIndex2 = listIndex2;
                        }
                    }
                    if (addIndex2 == -1) {
                        addIndex2 = listIndex2 + 1;
                    }
                    for (final PluginSubrecord mergeSubrecord2 : mergeSubrecordList) {
                        String subrecordType2 = mergeSubrecord2.getSubrecordType();
                        if (subrecordType2.equals("LVLO")) {
                            boolean addItem2 = true;
                            byte[] subrecordData2 = mergeSubrecord2.getSubrecordData();
                            final int level = SerializedElement.getShort(subrecordData2, 0);
                            int itemID = SerializedElement.getInteger(subrecordData2, 4);
                            itemID = mergeFormAdjust.adjustFormID(itemID);
                            if (startIndex2 >= 0) {
                                for (int l = startIndex2; l < addIndex2; ++l) {
                                    final PluginSubrecord checkSubrecord = currentSubrecordList.get(l);
                                    subrecordType2 = checkSubrecord.getSubrecordType();
                                    if (subrecordType2.equals("LVLO")) {
                                        final byte[] checkData = checkSubrecord.getSubrecordData();
                                        final int checkLevel = SerializedElement.getShort(checkData, 0);
                                        final int checkID3 = SerializedElement.getInteger(checkData, 4);
                                        if (checkID3 == itemID && checkLevel == level) {
                                            addItem2 = false;
                                            break;
                                        }
                                    }
                                }
                            }
                            if (!addItem2) {
                                continue;
                            }
                            final PluginSubrecord itemSubrecord = (PluginSubrecord)mergeSubrecord2.clone();
                            subrecordData2 = itemSubrecord.getSubrecordData();
                            SerializedElement.setInteger(itemID, subrecordData2, 4);
                            if (startIndex2 >= 0) {
                                for (int i2 = startIndex2; i2 < addIndex2; ++i2) {
                                    final PluginSubrecord checkSubrecord3 = currentSubrecordList.get(i2);
                                    subrecordType2 = checkSubrecord3.getSubrecordType();
                                    if (subrecordType2.equals("LVLO")) {
                                        final byte[] checkData3 = checkSubrecord3.getSubrecordData();
                                        final int checkLevel2 = SerializedElement.getShort(checkData3, 0);
                                        if (checkLevel2 > level) {
                                            currentSubrecordList.add(i2, itemSubrecord);
                                            ++addIndex2;
                                            addItem2 = false;
                                            break;
                                        }
                                    }
                                }
                            }
                            if (!addItem2) {
                                continue;
                            }
                            currentSubrecordList.add(addIndex2, itemSubrecord);
                            if (startIndex2 == -1) {
                                startIndex2 = addIndex2;
                            }
                            ++addIndex2;
                        }
                    }
                }
            }
            if (interrupted()) {
                throw new InterruptedException("Request canceled");
            }
        }
        return true;
    }
}
