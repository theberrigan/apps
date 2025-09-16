// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import javax.swing.tree.TreeNode;
import javax.swing.tree.MutableTreeNode;
import javax.swing.tree.DefaultMutableTreeNode;

public class GroupNode extends DefaultMutableTreeNode implements Comparable<GroupNode>
{
    public GroupNode(final PluginGroup group) {
        super(group);
    }
    
    public PluginGroup getGroup() {
        return (PluginGroup)this.getUserObject();
    }
    
    public void insert(final GroupNode groupNode) {
        int count;
        int index;
        for (count = this.getChildCount(), index = 0; index < count; ++index) {
            final TreeNode node = this.getChildAt(index);
            if (!(node instanceof GroupNode)) {
                break;
            }
            if (groupNode.compareTo((GroupNode)node) < 0) {
                break;
            }
        }
        this.insert(groupNode, index);
    }
    
    public void insert(final RecordNode recordNode) {
        int count;
        int index;
        for (count = this.getChildCount(), index = 0; index < count; ++index) {
            final TreeNode node = this.getChildAt(index);
            if (node instanceof RecordNode) {
                if (recordNode.compareTo((RecordNode)node) < 0) {
                    break;
                }
            }
        }
        this.insert(recordNode, index);
    }
    
    @Override
    public int hashCode() {
        return this.getGroup().hashCode();
    }
    
    @Override
    public boolean equals(final Object obj) {
        return obj instanceof GroupNode && this.getGroup().equals(((GroupNode)obj).getGroup());
    }
    
    @Override
    public int compareTo(final GroupNode node) {
        return this.getGroup().toString().compareTo(node.getGroup().toString());
    }
}
