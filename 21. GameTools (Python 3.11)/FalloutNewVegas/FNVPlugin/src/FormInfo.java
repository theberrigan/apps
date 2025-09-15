// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

public class FormInfo
{
    private PluginRecord record;
    private int mergedFormID;
    private String mergedEditorID;
    
    public FormInfo(final PluginRecord record) {
        this.record = record;
        this.mergedFormID = record.getFormID();
        this.mergedEditorID = record.getEditorID();
    }
    
    public PluginRecord getRecord() {
        return this.record;
    }
    
    public void setRecord(final PluginRecord record) {
        this.record = record;
    }
    
    public String getRecordType() {
        return this.record.getRecordType();
    }
    
    public int getFormID() {
        return this.record.getFormID();
    }
    
    public String getEditorID() {
        return this.record.getEditorID();
    }
    
    public int getMergedFormID() {
        return this.mergedFormID;
    }
    
    public void setMergedFormID(final int formID) {
        this.mergedFormID = formID;
    }
    
    public String getMergedEditorID() {
        return this.mergedEditorID;
    }
    
    public void setMergedEditorID(final String editorID) {
        this.mergedEditorID = editorID;
    }
}
