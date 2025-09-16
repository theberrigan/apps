// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import java.awt.event.ActionEvent;
import javax.swing.Box;
import javax.swing.BorderFactory;
import java.awt.LayoutManager;
import java.awt.Container;
import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JPanel;
import java.awt.Component;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import java.awt.Frame;
import javax.swing.JFrame;
import java.awt.event.ActionListener;
import javax.swing.JDialog;

public class DisplaySubrecordDialog extends JDialog implements ActionListener
{
    public DisplaySubrecordDialog(final JFrame parent, final PluginSubrecord subrecord) {
        super(parent, "Subrecord Data", true);
        this.setDefaultCloseOperation(2);
        final byte[] subrecordData = subrecord.getSubrecordData();
        final StringBuilder dumpData = new StringBuilder(128 + 3 * subrecordData.length + 6 * (subrecordData.length / 16));
        dumpData.append(String.format("%s subrecord: Data length x'%X'\n", subrecord.getSubrecordType(), subrecordData.length));
        dumpData.append("\n       0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F\n");
        final StringBuilder dumpHex = new StringBuilder(48);
        final StringBuilder dumpLine = new StringBuilder(16);
        int rows = 3;
        for (int i = 0; i < subrecordData.length; i += 16) {
            for (int j = 0; j < 16; ++j) {
                final int offset = i + j;
                if (offset == subrecordData.length) {
                    break;
                }
                dumpHex.append(String.format(" %02X", subrecordData[offset]));
                if (subrecordData[offset] >= 32 && subrecordData[offset] < 127) {
                    dumpLine.append(new String(subrecordData, offset, 1));
                }
                else {
                    dumpLine.append(".");
                }
            }
            while (dumpHex.length() < 48) {
                dumpHex.append("   ");
            }
            while (dumpLine.length() < 16) {
                dumpLine.append(" ");
            }
            dumpData.append(String.format("%04X:", i));
            dumpData.append((CharSequence)dumpHex);
            dumpData.append("  *");
            dumpData.append((CharSequence)dumpLine);
            dumpData.append("*");
            if (i + 16 < subrecordData.length) {
                dumpData.append("\n");
            }
            dumpHex.delete(0, 48);
            dumpLine.delete(0, 16);
            ++rows;
        }
        final JTextArea textArea = new JTextArea(dumpData.toString());
        textArea.setRows(Math.min(rows, 20));
        final JScrollPane scrollPane = new JScrollPane(textArea);
        scrollPane.setVerticalScrollBarPolicy(22);
        final JPanel buttonPane = new JPanel();
        final JButton button = new JButton("Done");
        button.setActionCommand("done");
        button.setHorizontalAlignment(0);
        button.addActionListener(this);
        buttonPane.add(button);
        final JPanel contentPane = new JPanel();
        contentPane.setLayout(new BoxLayout(contentPane, 1));
        contentPane.setOpaque(true);
        contentPane.setBorder(BorderFactory.createEmptyBorder(30, 30, 30, 30));
        contentPane.add(scrollPane);
        contentPane.add(Box.createVerticalStrut(15));
        contentPane.add(buttonPane);
        this.setContentPane(contentPane);
    }
    
    public static void showDialog(final JFrame parent, final PluginSubrecord subrecord) {
        final DisplaySubrecordDialog dialog = new DisplaySubrecordDialog(parent, subrecord);
        dialog.pack();
        dialog.setLocationRelativeTo(parent);
        dialog.setVisible(true);
    }
    
    @Override
    public void actionPerformed(final ActionEvent ae) {
        try {
            final String action = ae.getActionCommand();
            if (action.equals("done")) {
                this.setVisible(false);
                this.dispose();
            }
        }
        catch (Throwable exc) {
            Main.logException("Exception while processing action event", exc);
        }
    }
}
