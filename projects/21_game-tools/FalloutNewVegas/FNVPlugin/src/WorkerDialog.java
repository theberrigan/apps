// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import javax.swing.SwingUtilities;
import javax.swing.Icon;
import javax.swing.JOptionPane;
import java.awt.Component;

public class WorkerDialog implements Runnable
{
    public static final int CLOSED_OPTION = -1;
    public static final int OK_OPTION = 0;
    public static final int YES_OPTION = 0;
    public static final int NO_OPTION = 1;
    public static final int YES_TO_ALL_OPTION = 2;
    private boolean confirmDialog;
    private Component parent;
    private String message;
    private String title;
    private int optionType;
    private int messageType;
    private int selection;
    private boolean yesToAll;
    
    public WorkerDialog(final Component parent, final String message, final String title, final int messageType) {
        this.parent = parent;
        this.message = message;
        this.title = title;
        this.messageType = messageType;
        this.confirmDialog = false;
    }
    
    public WorkerDialog(final Component parent, final String message, final String title, final int optionType, final int messageType, final boolean yesToAll) {
        this.parent = parent;
        this.message = message;
        this.title = title;
        this.optionType = optionType;
        this.messageType = messageType;
        this.yesToAll = yesToAll;
        this.confirmDialog = true;
    }
    
    @Override
    public void run() {
        if (this.confirmDialog) {
            if (this.yesToAll) {
                final Object[] options = { "Yes", "No", "Yes to All" };
                this.selection = JOptionPane.showOptionDialog(this.parent, this.message, this.title, this.optionType, this.messageType, null, options, options[2]);
            }
            else {
                this.selection = JOptionPane.showConfirmDialog(this.parent, this.message, this.title, this.optionType, this.messageType);
            }
        }
        else {
            JOptionPane.showMessageDialog(this.parent, this.message, this.title, this.messageType);
            this.selection = 0;
        }
    }
    
    public int getSelection() {
        return this.selection;
    }
    
    public static void showMessageDialog(final Component parent, final String message, final String title, final int messageType) {
        final int selection = -1;
        try {
            final WorkerDialog messageDialog = new WorkerDialog(parent, message, title, messageType);
            SwingUtilities.invokeAndWait(messageDialog);
        }
        catch (InterruptedException exc) {
            Main.logException("Message dialog interrupted", exc);
        }
        catch (Throwable exc2) {
            Main.logException("Exception while displaying message dialog", exc2);
        }
    }
    
    public static int showConfirmDialog(final Component parent, final String message, final String title, final int optionType, final int messageType, final boolean yesToAll) {
        int selection = -1;
        try {
            final WorkerDialog confirmDialog = new WorkerDialog(parent, message, title, optionType, messageType, yesToAll);
            SwingUtilities.invokeAndWait(confirmDialog);
            selection = confirmDialog.getSelection();
        }
        catch (InterruptedException exc) {
            Main.logException("Confirmation dialog interrupted", exc);
        }
        catch (Throwable exc2) {
            Main.logException("Exception while displaying confirmation dialog", exc2);
        }
        return selection;
    }
}
