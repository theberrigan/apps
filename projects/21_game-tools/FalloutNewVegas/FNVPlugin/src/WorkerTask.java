// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import java.awt.Component;

public class WorkerTask extends Thread
{
    private StatusDialog statusDialog;
    
    public WorkerTask(final StatusDialog statusDialog) {
        this.statusDialog = statusDialog;
    }
    
    public StatusDialog getStatusDialog() {
        return this.statusDialog;
    }
    
    public Component getParent() {
        return this.statusDialog;
    }
}
