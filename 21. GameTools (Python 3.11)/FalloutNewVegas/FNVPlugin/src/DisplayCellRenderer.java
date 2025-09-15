// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import java.awt.Component;
import javax.swing.JTree;
import javax.swing.JTable;
import java.awt.Color;
import javax.swing.tree.DefaultTreeCellRenderer;

public class DisplayCellRenderer extends DefaultTreeCellRenderer
{
    private static final Color masterShading;
    private JTable masterTable;
    
    public DisplayCellRenderer(final JTable masterTable) {
        this.masterTable = masterTable;
        this.setTextSelectionColor(Color.WHITE);
        this.setTextNonSelectionColor(Color.BLACK);
        this.setBackgroundSelectionColor(Color.BLUE);
        this.setBackgroundNonSelectionColor(Color.WHITE);
    }
    
    @Override
    public Component getTreeCellRendererComponent(final JTree tree, final Object value, final boolean isSelected, final boolean isExpanded, final boolean isLeaf, final int row, final boolean hasFocus) {
        final Component component = super.getTreeCellRendererComponent(tree, value, isSelected, isExpanded, isLeaf, row, hasFocus);
        if (value instanceof RecordNode) {
            this.setBackgroundNonSelectionColor((((RecordNode)value).getRecord().getFormID() >>> 24 < this.masterTable.getRowCount()) ? DisplayCellRenderer.masterShading : Color.WHITE);
        }
        else {
            this.setBackgroundNonSelectionColor(Color.WHITE);
        }
        return component;
    }
    
    static {
        masterShading = new Color(255, 255, 192);
    }
}
