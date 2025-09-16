// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import javax.swing.tree.DefaultMutableTreeNode;

public class SubrecordNode extends DefaultMutableTreeNode
{
    public SubrecordNode(final PluginSubrecord subrecord) {
        super(subrecord);
    }
    
    public PluginSubrecord getSubrecord() {
        return (PluginSubrecord)this.getUserObject();
    }
}
