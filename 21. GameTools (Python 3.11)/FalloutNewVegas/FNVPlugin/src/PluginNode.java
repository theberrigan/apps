// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import java.util.Iterator;
import java.util.List;
import javax.swing.tree.MutableTreeNode;
import java.util.Map;
import java.util.HashMap;
import javax.swing.tree.DefaultMutableTreeNode;

public class PluginNode extends DefaultMutableTreeNode
{
    private HashMap<Integer, RecordNode> recordMap;
    
    public PluginNode(final Plugin plugin) {
        super(plugin);
        this.recordMap = new HashMap<Integer, RecordNode>(plugin.getRecordCount());
    }
    
    public Plugin getPlugin() {
        return (Plugin)this.getUserObject();
    }
    
    public Map<Integer, RecordNode> getRecordMap() {
        return this.recordMap;
    }
    
    public void insert(final GroupNode groupNode) {
        int count;
        int index;
        for (count = this.getChildCount(), index = 0; index < count && groupNode.compareTo((GroupNode)this.getChildAt(index)) >= 0; ++index) {}
        this.insert(groupNode, index);
    }
    
    public void buildNodes(final WorkerTask task) throws InterruptedException {
        final StatusDialog statusDialog = (task != null) ? task.getStatusDialog() : null;
        final List<PluginGroup> groupList = this.getPlugin().getGroupList();
        if (statusDialog != null) {
            statusDialog.updateMessage("Creating tree for " + this.getPlugin().getName());
        }
        this.removeAllChildren();
        for (final PluginGroup group : groupList) {
            final GroupNode groupNode = new GroupNode(group);
            this.createGroupChildren(groupNode, group);
            this.insert(groupNode);
            if (task != null && Thread.interrupted()) {
                throw new InterruptedException("Request canceled");
            }
        }
    }
    
    private void createGroupChildren(final GroupNode groupNode, final PluginGroup group) {
        final List<SerializedElement> recordList = group.getRecordList();
        for (final SerializedElement element : recordList) {
            if (element instanceof PluginGroup) {
                final PluginGroup subgroup = (PluginGroup)element;
                final GroupNode subgroupNode = new GroupNode(subgroup);
                this.createGroupChildren(subgroupNode, subgroup);
                groupNode.add(subgroupNode);
            }
            else {
                final PluginRecord record = (PluginRecord)element;
                final RecordNode recordNode = new RecordNode(record);
                if (record.getSubrecords().size() != 0) {
                    recordNode.add(new SubrecordNode(null));
                }
                this.recordMap.put(new Integer(record.getFormID()), recordNode);
                final int groupType = group.getGroupType();
                if (groupType == 0) {
                    final String recordType = group.getGroupRecordType();
                    if (recordType.equals("CELL") || recordType.equals("DIAL") || recordType.equals("WRLD")) {
                        groupNode.add(recordNode);
                    }
                    else {
                        groupNode.insert(recordNode);
                    }
                }
                else if (groupType == 10 || groupType == 8 || groupType == 9) {
                    groupNode.insert(recordNode);
                }
                else {
                    groupNode.add(recordNode);
                }
            }
        }
    }
    
    @Override
    public String toString() {
        final Plugin plugin = (Plugin)this.getUserObject();
        final String desc = String.format("%s (%s Version %.2f)", plugin.getName(), plugin.isMaster() ? "Master" : "Plugin", new Float(plugin.getPluginVersion()));
        return desc;
    }
}
