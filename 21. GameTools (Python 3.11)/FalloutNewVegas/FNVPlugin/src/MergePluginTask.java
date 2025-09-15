// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import java.util.ListIterator;
import java.util.Map;
import java.util.Iterator;
import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;
import java.io.IOException;
import java.util.zip.DataFormatException;
import javax.swing.JOptionPane;
import javax.swing.JDialog;
import javax.swing.JFrame;
import java.awt.Component;
import java.io.File;

public class MergePluginTask extends WorkerTask
{
    private Plugin plugin;
    private File[] mergeFiles;
    private PluginNode mergedNode;
    private boolean yesToAll;
    
    public MergePluginTask(final StatusDialog statusDialog, final Plugin plugin, final File[] mergeFiles) {
        super(statusDialog);
        this.yesToAll = false;
        this.plugin = plugin;
        this.mergeFiles = mergeFiles;
    }
    
    public static PluginNode mergePlugin(final Component parent, final Plugin plugin, final File[] mergeFiles) {
        StatusDialog statusDialog;
        if (parent instanceof JFrame) {
            statusDialog = new StatusDialog((JFrame)parent, "Cloning current plugin", "Merge Plugins");
        }
        else {
            statusDialog = new StatusDialog((JDialog)parent, "Cloning current plugin", "Merge Plugins");
        }
        final MergePluginTask worker = new MergePluginTask(statusDialog, plugin, mergeFiles);
        statusDialog.setWorker(worker);
        worker.start();
        statusDialog.showDialog();
        if (statusDialog.getStatus() != 1) {
            worker.mergedNode = null;
            JOptionPane.showMessageDialog(parent, "Unable to merge plugins", "Merge Plugins", 1);
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
        catch (InterruptedException exc5) {
            WorkerDialog.showMessageDialog(this.getStatusDialog(), "Request canceled", "Interrupted", 0);
        }
        catch (OperationCanceledException exc6) {}
        catch (Throwable exc4) {
            Main.logException("Exception while merging plugin", exc4);
        }
        statusDialog.closeDialog(completed);
    }
    
    private boolean processPlugin(final Plugin currentPlugin, final File mergeFile) throws DataFormatException, InterruptedException, IOException, OperationCanceledException, PluginException {
        final StatusDialog statusDialog = this.getStatusDialog();
        final Plugin mergePlugin = new Plugin(mergeFile);
        mergePlugin.load(this);
        statusDialog.updateMessage("Merging " + mergeFile.getName());
        final List<MasterEntry> masterList = currentPlugin.getMasterList();
        int masterCount = masterList.size();
        for (final MasterEntry masterEntry : masterList) {
            if (masterEntry.getName().equalsIgnoreCase(mergePlugin.getName())) {
                WorkerDialog.showMessageDialog(statusDialog, mergePlugin.getName() + " is in the master list for " + currentPlugin.getName(), "Dependent Plugin", 0);
                return false;
            }
        }
        final List<MasterEntry> mergeMasterList = mergePlugin.getMasterList();
        final int mergeMasterCount = mergeMasterList.size();
        boolean masterListChanged = false;
        for (final MasterEntry masterEntry2 : mergeMasterList) {
            final String masterName = masterEntry2.getName();
            if (!masterName.equalsIgnoreCase(currentPlugin.getName())) {
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
                masterList.add((MasterEntry)masterEntry2.clone());
                masterListChanged = true;
            }
        }
        final int[] masterAdjust = new int[masterCount];
        for (int i = 0; i < masterCount; ++i) {
            masterAdjust[i] = i;
        }
        masterCount = masterList.size();
        final int[] mergeMasterAdjust = new int[mergeMasterCount];
        for (int j = 0; j < mergeMasterCount; ++j) {
            final String masterName2 = mergeMasterList.get(j).getName();
            if (masterName2.equalsIgnoreCase(currentPlugin.getName())) {
                mergeMasterAdjust[j] = masterCount;
            }
            else {
                for (int k = 0; k < masterCount; ++k) {
                    final String checkName = masterList.get(k).getName();
                    if (checkName.equalsIgnoreCase(masterName2)) {
                        mergeMasterAdjust[j] = k;
                        break;
                    }
                }
            }
        }
        int highFormID = 0;
        FormAdjust formAdjust = new FormAdjust(masterAdjust, masterCount);
        List<PluginRecord> recordList = currentPlugin.getRecordList();
        int recordCount = recordList.size();
        final Map<Integer, PluginRecord> formIDMap = new HashMap<Integer, PluginRecord>(recordCount);
        final Map<String, PluginRecord> editorIDMap = new HashMap<String, PluginRecord>(recordCount);
        currentPlugin.getFormIDMap().clear();
        for (final PluginRecord record : recordList) {
            final int formID = record.getFormID();
            final int newFormID = formAdjust.adjustFormID(formID);
            if (masterListChanged) {
                record.updateReferences(formAdjust);
            }
            if (newFormID != formID) {
                record.changeFormID(newFormID);
            }
            formIDMap.put(new Integer(newFormID), record);
            currentPlugin.getFormIDMap().put(new Integer(newFormID), record);
            if (newFormID > highFormID) {
                highFormID = newFormID;
            }
            final String editorID = record.getEditorID();
            if (editorID.length() != 0) {
                editorIDMap.put(editorID.toLowerCase(), record);
            }
        }
        if (interrupted()) {
            throw new InterruptedException("Request canceled");
        }
        recordList = mergePlugin.getRecordList();
        recordCount = recordList.size();
        final List<FormInfo> formInfoList = new ArrayList<FormInfo>(recordCount);
        final Map<Integer, FormInfo> formInfoMap = new HashMap<Integer, FormInfo>(recordCount);
        for (final PluginRecord record2 : recordList) {
            if (record2.isIgnored()) {
                continue;
            }
            final int formID2 = record2.getFormID();
            final String editorID2 = record2.getEditorID();
            final FormInfo formInfo = new FormInfo(record2);
            formInfoList.add(formInfo);
            formInfoMap.put(new Integer(formID2), formInfo);
            final int masterIndex = formID2 >>> 24;
            if (masterIndex < mergeMasterCount) {
                continue;
            }
            if (record2.getRecordType().equals("GMST")) {
                final PluginRecord checkRecord = editorIDMap.get(editorID2.toLowerCase());
                if (checkRecord != null && checkRecord.getRecordType().equals("GMST")) {
                    formInfo.setMergedFormID(checkRecord.getFormID());
                    continue;
                }
            }
            int newFormID2 = (formID2 & 0xFFFFFF) | masterCount << 24;
            Integer objFormID = new Integer(newFormID2);
            boolean finalLoop = false;
            while (formIDMap.get(objFormID) != null) {
                if ((highFormID & 0xFFFFFF) == 0xFFFFFF) {
                    if (finalLoop) {
                        throw new PluginException("No form ID value available for assignment");
                    }
                    highFormID = (masterCount << 24 | 0x1);
                    finalLoop = true;
                }
                else {
                    ++highFormID;
                }
                newFormID2 = highFormID;
                objFormID = new Integer(newFormID2);
            }
            formInfo.setMergedFormID(newFormID2);
            formIDMap.put(objFormID, record2);
            if (editorID2.length() == 0) {
                continue;
            }
            String newEditorID;
            for (newEditorID = editorID2; editorIDMap.get(newEditorID.toLowerCase()) != null; newEditorID = newEditorID.concat("Z")) {}
            if (!newEditorID.equals(editorID2) && !this.yesToAll) {
                final String text = String.format("Editor ID '%s' already exists and will be changed to '%s'.  Do you want to continue?", editorID2, newEditorID);
                final int option = WorkerDialog.showConfirmDialog(statusDialog, text, "Editor ID Exists", 0, 2, true);
                if (option == 2) {
                    this.yesToAll = true;
                }
                else if (option != 0) {
                    throw new OperationCanceledException("Request canceled");
                }
            }
            formInfo.setMergedEditorID(newEditorID);
            editorIDMap.put(newEditorID.toLowerCase(), record2);
        }
        currentPlugin.setNextFormID((highFormID & 0xFFFFFF) + 1);
        if (interrupted()) {
            throw new InterruptedException("Request canceled");
        }
        final float mergeVersion = mergePlugin.getPluginVersion();
        final float currentVersion = currentPlugin.getPluginVersion();
        if (mergeVersion > currentVersion) {
            currentPlugin.setPluginVersion(mergeVersion);
        }
        recordList = currentPlugin.getRecordList();
        formAdjust = new FormAdjust(mergeMasterAdjust, masterCount, formInfoMap);
        for (final FormInfo formInfo2 : formInfoList) {
            final PluginRecord mergeRecord = formInfo2.getRecord();
            final int formID3 = formAdjust.adjustFormID(mergeRecord.getFormID());
            final PluginRecord record3 = formIDMap.get(new Integer(formID3));
            if (record3 == null) {
                currentPlugin.copyRecord(mergeRecord, formAdjust);
            }
            else if (record3 == mergeRecord) {
                if (!mergeRecord.isDeleted()) {
                    currentPlugin.copyRecord(mergeRecord, formAdjust);
                }
            }
            else {
                final int masterIndex2 = formID3 >>> 24;
                if (masterIndex2 >= masterCount && mergeRecord.isDeleted()) {
                    currentPlugin.removeRecord(record3);
                }
                else if (record3.getRecordType().equals("NAVI")) {
                    final PluginRecord pluginRecord = (PluginRecord)mergeRecord.clone();
                    pluginRecord.updateReferences(formAdjust);
                    this.mergeNavInfo(record3, pluginRecord);
                }
                else {
                    String editorID3 = formAdjust.adjustEditorID(mergeRecord.getFormID());
                    if (editorID3 == null) {
                        editorID3 = mergeRecord.getEditorID();
                    }
                    final PluginGroup pluginGroup = (PluginGroup)record3.getParent();
                    final PluginRecord pluginRecord2 = (PluginRecord)mergeRecord.clone();
                    pluginRecord2.setFormID(formID3);
                    pluginRecord2.setEditorID(editorID3);
                    pluginRecord2.setParent(pluginGroup);
                    pluginRecord2.updateReferences(formAdjust);
                    final List<SerializedElement> groupRecordList = pluginGroup.getRecordList();
                    int index = groupRecordList.indexOf(record3);
                    groupRecordList.set(index, pluginRecord2);
                    index = recordList.indexOf(record3);
                    recordList.set(index, pluginRecord2);
                    currentPlugin.getFormIDMap().put(new Integer(formID3), pluginRecord2);
                }
            }
            if (interrupted()) {
                throw new InterruptedException("Request canceled");
            }
        }
        currentPlugin.mergeVoiceFiles(mergePlugin, formInfoMap);
        return true;
    }
    
    private void mergeNavInfo(final PluginRecord record, final PluginRecord mergeRecord) throws PluginException {
        final List<PluginSubrecord> subrecordList = record.getSubrecords();
        final Map<Integer, PluginSubrecord> meshMap = new HashMap<Integer, PluginSubrecord>(subrecordList.size());
        final Map<Integer, PluginSubrecord> connMap = new HashMap<Integer, PluginSubrecord>(subrecordList.size());
        int meshVersion = 0;
        int index = -1;
        int meshIndex = -1;
        int connIndex = -1;
        for (final PluginSubrecord subrecord : subrecordList) {
            ++index;
            final byte[] subrecordData = subrecord.getSubrecordData();
            final String subrecordType = subrecord.getSubrecordType();
            if (subrecordType.equals("NVER")) {
                if (index != 0) {
                    throw new PluginException("NVER subrecord out of order");
                }
                if (subrecordData.length < 4) {
                    throw new PluginException(String.format("NVER subrecord length %d is too small", subrecordData.length));
                }
                meshVersion = SerializedElement.getInteger(subrecordData, 0);
            }
            else if (subrecordType.equals("NVMI")) {
                if (connIndex >= 0) {
                    throw new PluginException("NVMI subrecord out of order");
                }
                meshIndex = index;
                if (subrecordData.length < 8) {
                    throw new PluginException(String.format("NVMI subrecord length %d is too small", subrecordData.length));
                }
                final int formID = SerializedElement.getInteger(subrecordData, 4);
                final Integer objFormID = new Integer(formID);
                meshMap.put(objFormID, subrecord);
            }
            else {
                if (!subrecordType.equals("NVCI")) {
                    throw new PluginException("Unknown " + subrecordType + " subrecord for NAVI record");
                }
                if (meshIndex < 0) {
                    throw new PluginException("NVCI subrecord out of order");
                }
                connIndex = index;
                if (subrecordData.length < 4) {
                    throw new PluginException(String.format("NVCI subrecord length %d is too small", subrecordData.length));
                }
                final int formID = SerializedElement.getInteger(subrecordData, 0);
                final Integer objFormID = new Integer(formID);
                connMap.put(objFormID, subrecord);
            }
        }
        if (meshIndex == -1) {
            meshIndex = index;
            connIndex = index;
        }
        final List<PluginSubrecord> mergeSubrecordList = mergeRecord.getSubrecords();
        for (final PluginSubrecord subrecord2 : mergeSubrecordList) {
            final byte[] subrecordData2 = subrecord2.getSubrecordData();
            final String subrecordType2 = subrecord2.getSubrecordType();
            if (subrecordType2.equals("NVER")) {
                if (subrecordData2.length < 4) {
                    throw new PluginException(String.format("NVER subrecord length %d is too small", subrecordData2.length));
                }
                final int checkVersion = SerializedElement.getInteger(subrecordData2, 0);
                if (checkVersion != meshVersion) {
                    throw new PluginException(String.format("NAVI version mismatch: Current plugin %d, Merge plugin %d", meshVersion, checkVersion));
                }
                continue;
            }
            else if (subrecordType2.equals("NVMI")) {
                if (subrecordData2.length < 8) {
                    throw new PluginException(String.format("NVMI subrecord length %d is too small", subrecordData2.length));
                }
                final int formID2 = SerializedElement.getInteger(subrecordData2, 4);
                final Integer objFormID2 = new Integer(formID2);
                final PluginSubrecord checkSubrecord = meshMap.get(objFormID2);
                if (checkSubrecord == null) {
                    ++meshIndex;
                    ++connIndex;
                    subrecordList.add(meshIndex, subrecord2);
                    meshMap.put(objFormID2, subrecord2);
                }
                else {
                    final ListIterator<PluginSubrecord> li = subrecordList.listIterator();
                    while (li.hasNext()) {
                        final PluginSubrecord listSubrecord = li.next();
                        if (listSubrecord == checkSubrecord) {
                            li.set(subrecord2);
                            meshMap.put(objFormID2, subrecord2);
                            break;
                        }
                    }
                }
            }
            else {
                if (!subrecordType2.equals("NVCI")) {
                    throw new PluginException("Unknown " + subrecordType2 + " subrecord for NAVI record");
                }
                if (subrecordData2.length < 4) {
                    throw new PluginException(String.format("NVCI subrecord length %d is too small", subrecordData2.length));
                }
                final int formID2 = SerializedElement.getInteger(subrecordData2, 0);
                final Integer objFormID2 = new Integer(formID2);
                final PluginSubrecord checkSubrecord = connMap.get(objFormID2);
                if (checkSubrecord == null) {
                    ++connIndex;
                    subrecordList.add(connIndex, subrecord2);
                    connMap.put(objFormID2, subrecord2);
                }
                else {
                    final ListIterator<PluginSubrecord> li = subrecordList.listIterator();
                    while (li.hasNext()) {
                        final PluginSubrecord listSubrecord = li.next();
                        if (listSubrecord == checkSubrecord) {
                            li.set(subrecord2);
                            connMap.put(objFormID2, subrecord2);
                            break;
                        }
                    }
                }
            }
        }
    }
}
