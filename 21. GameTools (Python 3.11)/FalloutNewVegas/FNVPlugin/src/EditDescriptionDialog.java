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
import javax.swing.JScrollPane;
import java.awt.Component;
import javax.swing.JLabel;
import javax.swing.JPanel;
import java.awt.Dimension;
import java.awt.Frame;
import javax.swing.JFrame;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import java.awt.event.ActionListener;
import javax.swing.JDialog;

public class EditDescriptionDialog extends JDialog implements ActionListener
{
    private Plugin plugin;
    private JTextField creatorField;
    private JTextArea summaryField;
    private boolean descriptionUpdated;
    
    public EditDescriptionDialog(final JFrame parent, final Plugin plugin) {
        super(parent, "Edit Description", true);
        this.descriptionUpdated = false;
        this.setDefaultCloseOperation(2);
        this.plugin = plugin;
        final StringBuilder summary = new StringBuilder(plugin.getSummary());
        int index = 0;
        while (true) {
            index = summary.indexOf("\r\n", index);
            if (index < 0) {
                break;
            }
            summary.delete(index, index + 1);
            ++index;
        }
        final Dimension labelSize = new Dimension(70, 12);
        final JPanel creatorPane = new JPanel();
        JLabel label = new JLabel("Creator: ", 10);
        label.setPreferredSize(labelSize);
        this.creatorField = new JTextField(plugin.getCreator(), 32);
        creatorPane.add(label);
        creatorPane.add(this.creatorField);
        final JPanel summaryPane = new JPanel();
        label = new JLabel("Summary :", 10);
        label.setPreferredSize(labelSize);
        (this.summaryField = new JTextArea(summary.toString(), 8, 32)).setLineWrap(true);
        this.summaryField.setWrapStyleWord(true);
        this.summaryField.setFont(this.creatorField.getFont());
        final JScrollPane scrollPane = new JScrollPane(this.summaryField);
        summaryPane.add(label);
        summaryPane.add(scrollPane);
        final JPanel buttonPane = new JPanel();
        JButton button = new JButton("Update");
        button.setActionCommand("update");
        button.addActionListener(this);
        buttonPane.add(button);
        button = new JButton("Cancel");
        button.setActionCommand("cancel");
        button.addActionListener(this);
        buttonPane.add(button);
        final JPanel contentPane = new JPanel();
        contentPane.setLayout(new BoxLayout(contentPane, 1));
        contentPane.setBorder(BorderFactory.createEmptyBorder(30, 30, 30, 30));
        contentPane.add(creatorPane);
        contentPane.add(summaryPane);
        contentPane.add(Box.createVerticalStrut(15));
        contentPane.add(buttonPane);
        this.setContentPane(contentPane);
    }
    
    public static boolean showDialog(final JFrame parent, final Plugin plugin) {
        final EditDescriptionDialog dialog = new EditDescriptionDialog(parent, plugin);
        dialog.pack();
        dialog.setLocationRelativeTo(parent);
        dialog.setVisible(true);
        return dialog.descriptionUpdated;
    }
    
    @Override
    public void actionPerformed(final ActionEvent ae) {
        try {
            final String action = ae.getActionCommand();
            if (action.equals("update")) {
                String creator = this.creatorField.getText();
                final StringBuilder summary = new StringBuilder(this.summaryField.getText());
                if (creator.length() == 0) {
                    creator = new String("DEFAULT");
                }
                int index = 0;
                while (true) {
                    index = summary.indexOf("\n", index);
                    if (index < 0) {
                        break;
                    }
                    if (index == 0 || summary.charAt(index - 1) != '\r') {
                        summary.insert(index, "\r");
                        index += 2;
                    }
                    else {
                        ++index;
                    }
                }
                this.plugin.setCreator(creator);
                this.plugin.setSummary(summary.toString());
                this.descriptionUpdated = true;
                this.setVisible(false);
                this.dispose();
            }
            else if (action.equals("cancel")) {
                this.setVisible(false);
                this.dispose();
            }
        }
        catch (Throwable exc) {
            Main.logException("Exception while processing action event", exc);
        }
    }
}
