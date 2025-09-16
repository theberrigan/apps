// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import javax.swing.tree.DefaultMutableTreeNode;

public class RecordNode extends DefaultMutableTreeNode implements Comparable<RecordNode>
{
    public RecordNode(final PluginRecord record) {
        super(record);
    }
    
    public PluginRecord getRecord() {
        return (PluginRecord)this.getUserObject();
    }
    
    @Override
    public int hashCode() {
        return this.getRecord().hashCode();
    }
    
    @Override
    public boolean equals(final Object obj) {
        return obj instanceof RecordNode && this.getRecord().equals(((RecordNode)obj).getRecord());
    }
    
    @Override
    public int compareTo(final RecordNode node) {
        final PluginRecord record = this.getRecord();
        final PluginRecord cmpRecord = node.getRecord();
        int diff = record.getRecordType().compareTo(cmpRecord.getRecordType());
        if (diff == 0) {
            diff = record.getEditorID().compareTo(cmpRecord.getEditorID());
            if (diff == 0) {
                final int formID = record.getFormID();
                final int cmpFormID = cmpRecord.getFormID();
                if (formID < cmpFormID) {
                    diff = -1;
                }
                else if (formID > cmpFormID) {
                    diff = 1;
                }
            }
        }
        return diff;
    }
}
