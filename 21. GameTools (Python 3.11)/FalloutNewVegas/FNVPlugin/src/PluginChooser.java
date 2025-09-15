// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import javax.swing.JOptionPane;
import java.awt.event.ActionEvent;
import java.util.Iterator;
import java.util.List;
import javax.swing.Box;
import javax.swing.BorderFactory;
import java.awt.LayoutManager;
import java.awt.Container;
import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JPanel;
import java.awt.Component;
import javax.swing.JScrollPane;
import javax.swing.ListModel;
import java.util.ArrayList;
import java.io.IOException;
import java.awt.Frame;
import javax.swing.JFrame;
import java.io.File;
import javax.swing.JList;
import javax.swing.DefaultListModel;
import java.awt.event.ActionListener;
import javax.swing.JDialog;

public class PluginChooser extends JDialog implements ActionListener
{
    private static int SELECT_MASTER;
    private static int SELECT_PLUGIN;
    private static int SELECT_MULTIPLE;
    public static int SELECT_MASTER_SINGLE;
    public static int SELECT_PLUGIN_SINGLE;
    public static int SELECT_BOTH_SINGLE;
    public static int SELECT_MASTER_MULTIPLE;
    public static int SELECT_PLUGIN_MULTIPLE;
    public static int SELECT_BOTH_MULTIPLE;
    private DefaultListModel listModel;
    private JList fileList;
    private File[] pluginFiles;
    
    public PluginChooser(final JFrame parent, final int mode) throws IOException {
        super(parent, ((mode & PluginChooser.SELECT_MULTIPLE) != 0x0) ? "Select Files" : "Select File", true);
        this.pluginFiles = null;
        this.setDefaultCloseOperation(2);
        final File dir = new File(Main.pluginPath);
        if (!dir.exists() && !dir.mkdirs()) {
            throw new IOException("Unable to create directory '" + dir.getPath() + "'");
        }
        if (!dir.isDirectory()) {
            throw new IOException("'" + dir.getPath() + "' is not a directory");
        }
        this.listModel = new DefaultListModel();
        final File[] files = dir.listFiles();
        if (files != null) {
            final List<File> masterList = new ArrayList<File>(files.length);
            final List<File> pluginList = new ArrayList<File>(files.length);
            for (final File file : files) {
                if (file.isFile()) {
                    final String name = file.getName();
                    final long lastModified = file.lastModified();
                    final int sep = name.lastIndexOf(46);
                    if (sep > 0) {
                        final String ext = name.substring(sep);
                        boolean added = false;
                        if (ext.equalsIgnoreCase(".esm") && (mode & PluginChooser.SELECT_MASTER) != 0x0) {
                            for (int count = masterList.size(), i = 0; i < count; ++i) {
                                final File checkFile = masterList.get(i);
                                if (lastModified < checkFile.lastModified()) {
                                    masterList.add(i, file);
                                    added = true;
                                    break;
                                }
                            }
                            if (!added) {
                                masterList.add(file);
                            }
                        }
                        else if (ext.equalsIgnoreCase(".esp") && (mode & PluginChooser.SELECT_PLUGIN) != 0x0) {
                            for (int count = pluginList.size(), i = 0; i < count; ++i) {
                                final File checkFile = pluginList.get(i);
                                if (lastModified < checkFile.lastModified()) {
                                    pluginList.add(i, file);
                                    added = true;
                                    break;
                                }
                            }
                            if (!added) {
                                pluginList.add(file);
                            }
                        }
                    }
                }
            }
            for (final File file2 : masterList) {
                this.listModel.addElement(file2.getName());
            }
            for (final File file2 : pluginList) {
                this.listModel.addElement(file2.getName());
            }
        }
        this.fileList = new JList(this.listModel);
        if ((mode & PluginChooser.SELECT_MULTIPLE) != 0x0) {
            this.fileList.setSelectionMode(2);
        }
        else {
            this.fileList.setSelectionMode(0);
        }
        this.fileList.setVisibleRowCount(15);
        final JScrollPane scrollPane = new JScrollPane(this.fileList);
        final JPanel buttonPane = new JPanel();
        JButton button = new JButton("Select");
        button.setActionCommand("select");
        button.addActionListener(this);
        buttonPane.add(button);
        button = new JButton("Cancel");
        button.setActionCommand("cancel");
        button.addActionListener(this);
        buttonPane.add(button);
        final JPanel contentPane = new JPanel();
        contentPane.setLayout(new BoxLayout(contentPane, 1));
        contentPane.setBorder(BorderFactory.createEmptyBorder(30, 30, 30, 30));
        contentPane.add(scrollPane);
        contentPane.add(Box.createVerticalStrut(15));
        contentPane.add(buttonPane);
        this.setContentPane(contentPane);
    }
    
    public static File[] showDialog(final JFrame parent, final int mode) {
        File[] pluginFiles = null;
        try {
            final PluginChooser dialog = new PluginChooser(parent, mode);
            dialog.pack();
            dialog.setLocationRelativeTo(parent);
            dialog.setVisible(true);
            pluginFiles = dialog.pluginFiles;
        }
        catch (Exception exc) {
            Main.logException("Exception while displaying file list", exc);
        }
        return pluginFiles;
    }
    
    @Override
    public void actionPerformed(final ActionEvent ae) {
        try {
            final String action = ae.getActionCommand();
            if (action.equals("select")) {
                final Object[] names = this.fileList.getSelectedValues();
                if (names == null || names.length == 0) {
                    JOptionPane.showMessageDialog(this, "No file has been selected", "No File Selected", 0);
                }
                else {
                    this.pluginFiles = new File[names.length];
                    int index = 0;
                    for (final Object name : names) {
                        this.pluginFiles[index++] = new File(Main.pluginPath + Main.fileSeparator + (String)name);
                    }
                    this.setVisible(false);
                    this.dispose();
                }
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
    
    static {
        PluginChooser.SELECT_MASTER = 1;
        PluginChooser.SELECT_PLUGIN = 2;
        PluginChooser.SELECT_MULTIPLE = 4;
        PluginChooser.SELECT_MASTER_SINGLE = PluginChooser.SELECT_MASTER;
        PluginChooser.SELECT_PLUGIN_SINGLE = PluginChooser.SELECT_PLUGIN;
        PluginChooser.SELECT_BOTH_SINGLE = PluginChooser.SELECT_MASTER + PluginChooser.SELECT_PLUGIN;
        PluginChooser.SELECT_MASTER_MULTIPLE = PluginChooser.SELECT_MASTER + PluginChooser.SELECT_MULTIPLE;
        PluginChooser.SELECT_PLUGIN_MULTIPLE = PluginChooser.SELECT_PLUGIN + PluginChooser.SELECT_MULTIPLE;
        PluginChooser.SELECT_BOTH_MULTIPLE = PluginChooser.SELECT_MASTER + PluginChooser.SELECT_PLUGIN + PluginChooser.SELECT_MULTIPLE;
    }
}
