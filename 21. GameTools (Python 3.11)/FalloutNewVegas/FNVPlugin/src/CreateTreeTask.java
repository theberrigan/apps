// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import java.io.IOException;
import java.util.zip.DataFormatException;
import javax.swing.JOptionPane;
import javax.swing.JDialog;
import javax.swing.JFrame;
import java.awt.Component;
import java.io.File;

public class CreateTreeTask extends WorkerTask
{
    private File pluginFile;
    private Plugin plugin;
    private PluginNode pluginNode;
    
    public CreateTreeTask(final StatusDialog statusDialog, final File pluginFile) {
        super(statusDialog);
        this.pluginFile = pluginFile;
    }
    
    public static PluginNode createTree(final Component parent, final File pluginFile) {
        StatusDialog statusDialog;
        if (parent instanceof JFrame) {
            statusDialog = new StatusDialog((JFrame)parent, "Creating tree", "Create Tree");
        }
        else {
            statusDialog = new StatusDialog((JDialog)parent, "Creating tree", "Create Tree");
        }
        final CreateTreeTask worker = new CreateTreeTask(statusDialog, pluginFile);
        statusDialog.setWorker(worker);
        worker.start();
        statusDialog.showDialog();
        if (statusDialog.getStatus() != 1) {
            worker.pluginNode = null;
            JOptionPane.showMessageDialog(parent, "Unable to create tree for " + pluginFile.getName(), "Create Tree", 1);
        }
        return worker.pluginNode;
    }
    
    @Override
    public void run() {
        boolean completed = false;
        try {
            (this.plugin = new Plugin(this.pluginFile)).load(this);
            (this.pluginNode = new PluginNode(this.plugin)).buildNodes(this);
            completed = true;
        }
        catch (PluginException exc) {
            Main.logException("Plugin Error", exc);
        }
        catch (DataFormatException exc2) {
            Main.logException("Compression Error", exc2);
        }
        catch (IOException exc3) {
            Main.logException("I/O Error", exc3);
        }
        catch (InterruptedException exc5) {
            WorkerDialog.showMessageDialog(this.getStatusDialog(), "Request canceled", "Interrupted", 0);
        }
        catch (Throwable exc4) {
            Main.logException("Exception while creating tree", exc4);
        }
        this.getStatusDialog().closeDialog(completed);
    }
}
