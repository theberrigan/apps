// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import java.io.IOException;
import java.util.zip.DataFormatException;
import javax.swing.JDialog;
import javax.swing.JFrame;
import java.awt.Component;

public class SavePluginTask extends WorkerTask
{
    private PluginNode pluginNode;
    
    public SavePluginTask(final StatusDialog statusDialog, final PluginNode pluginNode) {
        super(statusDialog);
        this.pluginNode = pluginNode;
    }
    
    public static boolean savePlugin(final Component parent, final PluginNode pluginNode) {
        StatusDialog statusDialog;
        if (parent instanceof JFrame) {
            statusDialog = new StatusDialog((JFrame)parent, "Saving plugin", "Save Plugin");
        }
        else {
            statusDialog = new StatusDialog((JDialog)parent, "Saving plugin", "Save Plugin");
        }
        final SavePluginTask worker = new SavePluginTask(statusDialog, pluginNode);
        statusDialog.setWorker(worker);
        worker.start();
        statusDialog.showDialog();
        return statusDialog.getStatus() == 1;
    }
    
    @Override
    public void run() {
        boolean completed = false;
        try {
            final Plugin plugin = this.pluginNode.getPlugin();
            final int recordCount = plugin.getRecordCount();
            plugin.buildFormOverrides();
            plugin.store(this);
            if (plugin.getRecordCount() != recordCount) {
                this.pluginNode.buildNodes(this);
            }
            completed = true;
        }
        catch (DataFormatException exc) {
            Main.logException("Compression Error", exc);
        }
        catch (IOException exc2) {
            Main.logException("I/O Error", exc2);
        }
        catch (InterruptedException exc5) {
            WorkerDialog.showMessageDialog(this.getStatusDialog(), "Request canceled", "Interrupted", 0);
        }
        catch (PluginException exc3) {
            Main.logException("Plugin is not valid", exc3);
        }
        catch (Throwable exc4) {
            Main.logException("Exception while saving plugin", exc4);
        }
        this.getStatusDialog().closeDialog(completed);
    }
}
