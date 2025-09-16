// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import java.io.File;
import javax.swing.filechooser.FileFilter;

public class PluginFileFilter extends FileFilter
{
    private boolean includeMasterFiles;
    private boolean includePluginFiles;
    
    public PluginFileFilter() {
        this.includeMasterFiles = true;
        this.includePluginFiles = true;
    }
    
    @Override
    public String getDescription() {
        String desc;
        if (this.includeMasterFiles) {
            if (this.includePluginFiles) {
                desc = "Plugin files (*.esm, *.esp)";
            }
            else {
                desc = "Plugin files (*.esm)";
            }
        }
        else {
            desc = "Plugin files (*.esp)";
        }
        return desc;
    }
    
    @Override
    public boolean accept(final File file) {
        boolean accept = false;
        if (file.isFile()) {
            final String name = file.getName();
            final int sep = name.lastIndexOf(46);
            if (sep > 0) {
                final String extension = name.substring(sep).toLowerCase();
                if (extension.equals(".esm")) {
                    if (this.includeMasterFiles) {
                        accept = true;
                    }
                }
                else if (extension.equals(".esp") && this.includePluginFiles) {
                    accept = true;
                }
            }
        }
        else {
            accept = true;
        }
        return accept;
    }
}
