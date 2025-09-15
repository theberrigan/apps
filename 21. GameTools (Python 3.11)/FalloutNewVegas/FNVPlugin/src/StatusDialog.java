// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import javax.swing.SwingUtilities;
import java.awt.event.ActionEvent;
import javax.swing.Box;
import javax.swing.BorderFactory;
import java.awt.LayoutManager;
import java.awt.Container;
import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JPanel;
import java.awt.Dialog;
import java.awt.Frame;
import javax.swing.JFrame;
import javax.swing.JLabel;
import java.awt.Component;
import java.awt.event.ActionListener;
import javax.swing.JDialog;

public class StatusDialog extends JDialog implements ActionListener
{
    private Component parent;
    private Thread worker;
    private JLabel messageText;
    private int status;
    private String deferredText;
    
    public StatusDialog(final JFrame parent, final String text, final String title) {
        super(parent, title, true);
        this.status = -1;
        this.parent = parent;
        this.initFields(text);
    }
    
    public StatusDialog(final JDialog parent, final String text, final String title) {
        super(parent, title, true);
        this.status = -1;
        this.parent = parent;
        this.initFields(text);
    }
    
    private void initFields(final String text) {
        final JPanel messagePane = new JPanel();
        messagePane.add(this.messageText = new JLabel(text));
        final JPanel buttonPane = new JPanel();
        final JButton button = new JButton("Cancel");
        button.setActionCommand("cancel");
        button.addActionListener(this);
        buttonPane.add(button);
        final JPanel contentPane = new JPanel();
        contentPane.setLayout(new BoxLayout(contentPane, 1));
        contentPane.setBorder(BorderFactory.createEmptyBorder(15, 15, 15, 15));
        contentPane.add(messagePane);
        contentPane.add(Box.createVerticalStrut(15));
        contentPane.add(buttonPane);
        this.setContentPane(contentPane);
    }
    
    public void setWorker(final Thread worker) {
        this.worker = worker;
    }
    
    @Override
    public void actionPerformed(final ActionEvent ae) {
        try {
            final String action = ae.getActionCommand();
            if (action.equals("cancel") && this.worker != null) {
                this.worker.interrupt();
            }
        }
        catch (Throwable exc) {
            Main.logException("Exception while processing action event", exc);
        }
    }
    
    public int showDialog() {
        this.pack();
        this.setLocationRelativeTo(this.parent);
        while (this.status == -1) {
            this.setVisible(true);
        }
        return this.status;
    }
    
    public int getStatus() {
        return this.status;
    }
    
    public void closeDialog(final boolean completed) {
        this.status = (completed ? 1 : 0);
        if (SwingUtilities.isEventDispatchThread()) {
            this.setVisible(false);
            this.dispose();
        }
        else {
            SwingUtilities.invokeLater(new Runnable() {
                @Override
                public void run() {
                    StatusDialog.this.setVisible(false);
                    StatusDialog.this.dispose();
                }
            });
        }
    }
    
    public void updateMessage(final String text) {
        if (SwingUtilities.isEventDispatchThread()) {
            this.messageText.setText(text);
            this.pack();
            this.setLocationRelativeTo(this.parent);
        }
        else {
            this.deferredText = text;
            SwingUtilities.invokeLater(new Runnable() {
                @Override
                public void run() {
                    StatusDialog.this.messageText.setText(StatusDialog.this.deferredText);
                    StatusDialog.this.pack();
                    StatusDialog.this.setLocationRelativeTo(StatusDialog.this.parent);
                }
            });
        }
    }
}
