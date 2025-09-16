// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import java.awt.event.WindowEvent;
import java.awt.event.WindowAdapter;
import java.awt.Point;
import java.util.regex.Matcher;
import java.util.regex.PatternSyntaxException;
import java.util.regex.Pattern;
import java.io.RandomAccessFile;
import java.io.IOException;
import java.util.Iterator;
import java.util.List;
import javax.swing.tree.MutableTreeNode;
import javax.swing.tree.TreePath;
import javax.swing.event.TreeExpansionEvent;
import javax.swing.JOptionPane;
import java.awt.event.ActionEvent;
import java.awt.event.WindowStateListener;
import java.awt.event.WindowListener;
import javax.swing.tree.TreeCellRenderer;
import javax.swing.tree.TreeModel;
import javax.swing.tree.TreeNode;
import java.awt.Container;
import javax.swing.BoxLayout;
import java.awt.LayoutManager;
import java.awt.BorderLayout;
import javax.swing.JButton;
import javax.swing.Box;
import javax.swing.JScrollPane;
import javax.swing.table.TableModel;
import java.awt.Component;
import javax.swing.BorderFactory;
import java.awt.Color;
import javax.swing.JPanel;
import javax.swing.JMenuItem;
import javax.swing.JMenu;
import javax.swing.JMenuBar;
import java.awt.Dimension;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.JTextField;
import javax.swing.JLabel;
import javax.swing.JTable;
import javax.swing.table.DefaultTableModel;
import javax.swing.JTree;
import javax.swing.tree.DefaultTreeModel;
import java.io.File;
import javax.swing.event.TreeExpansionListener;
import java.awt.event.ActionListener;
import javax.swing.JFrame;

public class MainWindow extends JFrame implements ActionListener, TreeExpansionListener
{
    private ApplicationWindowListener windowListener;
    private Plugin plugin;
    private PluginNode pluginNode;
    private File pluginFile;
    private DefaultTreeModel pluginTreeModel;
    private JTree pluginTree;
    private String[] masterColumns;
    private DefaultTableModel masterTableModel;
    private JTable masterTable;
    private int masterCount;
    private JLabel pluginLabel;
    private JLabel countLabel;
    private JTextField searchField;
    private JTextField formField;
    private DefaultMutableTreeNode searchNode;
    
    public MainWindow() {
        super("Fallout New Vegas Plugin Utility");
        this.masterColumns = new String[] { "Index", "Master" };
        this.setDefaultCloseOperation(2);
        String propValue = Main.properties.getProperty("window.main.position");
        if (propValue != null) {
            final int sep = propValue.indexOf(44);
            final int frameX = Integer.parseInt(propValue.substring(0, sep));
            final int frameY = Integer.parseInt(propValue.substring(sep + 1));
            this.setLocation(frameX, frameY);
        }
        int frameWidth = 800;
        int frameHeight = 640;
        propValue = Main.properties.getProperty("window.main.size");
        if (propValue != null) {
            final int sep2 = propValue.indexOf(44);
            frameWidth = Integer.parseInt(propValue.substring(0, sep2));
            frameHeight = Integer.parseInt(propValue.substring(sep2 + 1));
        }
        this.setPreferredSize(new Dimension(frameWidth, frameHeight));
        final JMenuBar menuBar = new JMenuBar();
        JMenu menu = new JMenu("File");
        menu.setMnemonic(70);
        JMenuItem menuItem = new JMenuItem("New");
        menuItem.setActionCommand("new plugin");
        menuItem.addActionListener(this);
        menu.add(menuItem);
        menuItem = new JMenuItem("Open");
        menuItem.setActionCommand("open plugin");
        menuItem.addActionListener(this);
        menu.add(menuItem);
        menuItem = new JMenuItem("Save");
        menuItem.setActionCommand("save plugin");
        menuItem.addActionListener(this);
        menu.add(menuItem);
        menuItem = new JMenuItem("Save As");
        menuItem.setActionCommand("rename plugin");
        menuItem.addActionListener(this);
        menu.add(menuItem);
        menuItem = new JMenuItem("Close");
        menuItem.setActionCommand("close plugin");
        menuItem.addActionListener(this);
        menu.add(menuItem);
        menu.addSeparator();
        menuItem = new JMenuItem("Merge Lists");
        menuItem.setActionCommand("merge lists");
        menuItem.addActionListener(this);
        menu.add(menuItem);
        menuItem = new JMenuItem("Merge Plugins");
        menuItem.setActionCommand("merge plugins");
        menuItem.addActionListener(this);
        menu.add(menuItem);
        menu.addSeparator();
        menuItem = new JMenuItem("Exit");
        menuItem.setActionCommand("exit");
        menuItem.addActionListener(this);
        menu.add(menuItem);
        menuBar.add(menu);
        menu = new JMenu("Edit");
        menu.setMnemonic(69);
        menuItem = new JMenuItem("Edit Description");
        menuItem.setActionCommand("edit description");
        menuItem.addActionListener(this);
        menu.add(menuItem);
        menuItem = new JMenuItem("Toggle Master");
        menuItem.setActionCommand("toggle master");
        menuItem.addActionListener(this);
        menu.add(menuItem);
        menuItem = new JMenuItem("Toggle Master List");
        menuItem.setActionCommand("toggle master list");
        menuItem.addActionListener(this);
        menu.add(menuItem);
        menuBar.add(menu);
        menu = new JMenu("Help");
        menu.setMnemonic(72);
        menuItem = new JMenuItem("About");
        menuItem.setActionCommand("about");
        menuItem.addActionListener(this);
        menu.add(menuItem);
        menuBar.add(menu);
        this.setJMenuBar(menuBar);
        this.countLabel = new JLabel("Plugin record count: 0");
        final JPanel countPane = new JPanel();
        countPane.setBorder(BorderFactory.createEtchedBorder(Color.WHITE, Color.BLACK));
        countPane.add(this.countLabel);
        countPane.setMaximumSize(new Dimension(200, 30));
        this.masterTableModel = new DefaultTableModel(new String[0][2], this.masterColumns);
        (this.masterTable = new JTable(this.masterTableModel)).setColumnSelectionAllowed(false);
        this.masterTable.setRowSelectionAllowed(false);
        this.masterTable.getColumnModel().getColumn(0).setMaxWidth(50);
        this.masterTable.setAutoResizeMode(3);
        this.masterTable.setPreferredScrollableViewportSize(new Dimension(250, this.masterTable.getRowHeight() * Math.max(this.masterCount, 1)));
        final JScrollPane masterScrollPane = new JScrollPane(this.masterTable);
        JLabel searchLabel = new JLabel("Editor ID Search");
        searchLabel.setHorizontalAlignment(0);
        (this.searchField = new JTextField(20)).setActionCommand("find editor id");
        this.searchField.addActionListener(this);
        JPanel buttonPane = new JPanel();
        buttonPane.add(Box.createGlue());
        JButton button = new JButton("Find");
        button.setActionCommand("find editor id");
        button.addActionListener(this);
        buttonPane.add(button);
        buttonPane.add(Box.createHorizontalStrut(10));
        button = new JButton("Find Next");
        button.setActionCommand("find next editor id");
        button.addActionListener(this);
        buttonPane.add(button);
        buttonPane.add(Box.createGlue());
        BorderLayout searchLayout = new BorderLayout();
        searchLayout.setVgap(10);
        final JPanel searchPane = new JPanel(searchLayout);
        searchPane.setBorder(BorderFactory.createEtchedBorder(Color.WHITE, Color.BLACK));
        searchPane.add(searchLabel, "North");
        searchPane.add(this.searchField, "Center");
        searchPane.add(buttonPane, "South");
        searchPane.setMaximumSize(new Dimension(200, 50));
        searchLabel = new JLabel("Form ID Search");
        searchLabel.setHorizontalAlignment(0);
        (this.formField = new JTextField(10)).setActionCommand("find form id");
        this.formField.addActionListener(this);
        button = new JButton("Find");
        button.setActionCommand("find form id");
        button.addActionListener(this);
        buttonPane = new JPanel();
        buttonPane.add(Box.createGlue());
        buttonPane.add(button);
        buttonPane.add(Box.createGlue());
        searchLayout = new BorderLayout();
        searchLayout.setVgap(10);
        final JPanel formPane = new JPanel(searchLayout);
        formPane.setBorder(BorderFactory.createEtchedBorder(Color.WHITE, Color.BLACK));
        formPane.add(searchLabel, "North");
        formPane.add(this.formField, "Center");
        formPane.add(buttonPane, "South");
        formPane.setMaximumSize(new Dimension(200, 50));
        final JPanel sidePane = new JPanel();
        sidePane.setLayout(new BoxLayout(sidePane, 1));
        sidePane.add(Box.createGlue());
        sidePane.add(countPane);
        sidePane.add(Box.createVerticalStrut(25));
        sidePane.add(masterScrollPane);
        sidePane.add(Box.createVerticalStrut(25));
        sidePane.add(searchPane);
        sidePane.add(Box.createVerticalStrut(25));
        sidePane.add(formPane);
        sidePane.add(Box.createVerticalStrut(25));
        sidePane.add(Box.createGlue());
        this.pluginTreeModel = new DefaultTreeModel(this.pluginNode);
        (this.pluginTree = new JTree(this.pluginTreeModel)).setCellRenderer(new DisplayCellRenderer(this.masterTable));
        this.pluginTree.setScrollsOnExpand(true);
        this.pluginTree.setExpandsSelectedPaths(true);
        this.pluginTree.addTreeExpansionListener(this);
        final JScrollPane pluginScrollPane = new JScrollPane(this.pluginTree);
        pluginScrollPane.setHorizontalScrollBarPolicy(32);
        pluginScrollPane.setVerticalScrollBarPolicy(22);
        pluginScrollPane.setPreferredSize(new Dimension(500, 500));
        this.pluginLabel = new JLabel();
        final JPanel labelPane = new JPanel();
        labelPane.add(this.pluginLabel);
        buttonPane = new JPanel();
        button = new JButton("Display Subrecord");
        button.setActionCommand("display subrecord");
        button.addActionListener(this);
        buttonPane.add(button);
        button = new JButton("Toggle Ignore");
        button.setActionCommand("toggle ignore");
        button.addActionListener(this);
        buttonPane.add(button);
        final JPanel pluginPane = new JPanel();
        pluginPane.setLayout(new BoxLayout(pluginPane, 1));
        pluginPane.setBorder(BorderFactory.createEtchedBorder(Color.WHITE, Color.BLACK));
        pluginPane.add(labelPane);
        pluginPane.add(pluginScrollPane);
        pluginPane.add(Box.createVerticalStrut(10));
        pluginPane.add(buttonPane);
        final JPanel treePane = new JPanel();
        treePane.setLayout(new BoxLayout(treePane, 0));
        treePane.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));
        treePane.add(sidePane);
        treePane.add(Box.createHorizontalStrut(15));
        treePane.add(pluginPane);
        this.setContentPane(treePane);
        this.addWindowListener(this.windowListener = new ApplicationWindowListener());
        this.addWindowStateListener(this.windowListener);
    }
    
    @Override
    public void actionPerformed(final ActionEvent ae) {
        try {
            final String action = ae.getActionCommand();
            if (action.equals("open plugin")) {
                this.openPlugin();
            }
            else if (action.equals("new plugin")) {
                this.newPlugin();
            }
            else if (action.equals("exit")) {
                this.exitProgram();
            }
            else if (action.equals("about")) {
                this.aboutProgram();
            }
            else if (this.plugin == null) {
                JOptionPane.showMessageDialog(this, "You must open a plugin", "No plugin open", 0);
            }
            else if (action.equals("merge plugins")) {
                this.mergePlugins();
            }
            else if (action.equals("merge lists")) {
                this.mergeLists();
            }
            else if (action.equals("save plugin")) {
                this.savePlugin();
            }
            else if (action.equals("rename plugin")) {
                this.renamePlugin();
            }
            else if (action.equals("close plugin")) {
                this.closePlugin();
            }
            else if (action.equals("edit description")) {
                this.editDescription();
            }
            else if (action.equals("toggle master")) {
                this.toggleMaster();
            }
            else if (action.equals("toggle master list")) {
                this.toggleMasterList();
            }
            else if (action.equals("display subrecord")) {
                this.displaySubrecordData();
            }
            else if (action.equals("toggle ignore")) {
                this.toggleIgnore();
            }
            else if (action.equals("find editor id")) {
                this.findEditorID(false);
            }
            else if (action.equals("find next editor id")) {
                this.findEditorID(true);
            }
            else if (action.equals("find form id")) {
                this.findFormID();
            }
        }
        catch (Throwable exc) {
            Main.logException("Exception while processing action event", exc);
        }
    }
    
    @Override
    public void treeExpanded(final TreeExpansionEvent event) {
        final JTree tree = (JTree)event.getSource();
        final TreePath treePath = event.getPath();
        final DefaultMutableTreeNode node = (DefaultMutableTreeNode)treePath.getLastPathComponent();
        if (node instanceof RecordNode) {
            final RecordNode recordNode = (RecordNode)node;
            final SubrecordNode subrecordNode = (SubrecordNode)recordNode.getFirstChild();
            if (subrecordNode.getSubrecord() == null) {
                try {
                    recordNode.removeAllChildren();
                    this.createRecordChildren(recordNode);
                    final DefaultTreeModel model = (DefaultTreeModel)tree.getModel();
                    model.nodeStructureChanged(recordNode);
                }
                catch (Throwable exc) {
                    Main.logException("Exception while creating subrecords", exc);
                }
            }
        }
    }
    
    private void createRecordChildren(final RecordNode recordNode) {
        final List<PluginSubrecord> subrecordList = recordNode.getRecord().getSubrecords();
        for (final PluginSubrecord subrecord : subrecordList) {
            final SubrecordNode subrecordNode = new SubrecordNode(subrecord);
            recordNode.add(subrecordNode);
        }
    }
    
    @Override
    public void treeCollapsed(final TreeExpansionEvent event) {
    }
    
    private void updateTitle() {
        if (this.plugin == null) {
            super.setTitle("Fallout 3 Plugin Utility");
        }
        else if (Main.pluginModified) {
            super.setTitle("Fallout 3 Plugin Utility - " + this.plugin.getName() + "*");
        }
        else {
            super.setTitle("Fallout 3 Plugin Utility - " + this.plugin.getName());
        }
    }
    
    private void updateDisplay() {
        this.pluginLabel.setText(this.plugin.getName());
        this.pluginTreeModel = new DefaultTreeModel(this.pluginNode);
        this.pluginTree.setModel(this.pluginTreeModel);
        final List<MasterEntry> masterList = this.plugin.getMasterList();
        final int count = masterList.size();
        final String[][] masterNames = new String[count][2];
        for (int i = 0; i < count; ++i) {
            masterNames[i][0] = String.format("%02X", i);
            masterNames[i][1] = masterList.get(i).getName();
        }
        this.masterTableModel = new DefaultTableModel(masterNames, this.masterColumns);
        this.masterTable.setModel(this.masterTableModel);
        this.masterTable.getColumnModel().getColumn(0).setMaxWidth(50);
        this.masterTable.setAutoResizeMode(3);
        this.countLabel.setText("Plugin record count: " + this.plugin.getRecordCount());
        this.updateTitle();
    }
    
    private void newPlugin() {
        String pluginName = null;
        boolean master = false;
        if (!this.closePlugin()) {
            return;
        }
        while (true) {
            pluginName = JOptionPane.showInputDialog(this, "Enter the name for the new plugin");
            if (pluginName == null || pluginName.length() == 0) {
                return;
            }
            if (pluginName.indexOf(47) < 0 && pluginName.indexOf(92) < 0) {
                final int sep = pluginName.lastIndexOf(46);
                if (sep < 0) {
                    pluginName = pluginName.concat(".esp");
                }
                else {
                    final String ext = pluginName.substring(sep);
                    if (ext.equalsIgnoreCase(".esm")) {
                        master = true;
                    }
                    else if (!ext.equalsIgnoreCase(".esp")) {
                        pluginName = pluginName.concat(".esp");
                    }
                }
                final File pluginFile = new File(Main.pluginPath + Main.fileSeparator + pluginName);
                if (pluginFile.exists()) {
                    final int option = JOptionPane.showConfirmDialog(this, "'" + pluginName + "' already exists.  Do you want to overwrite it?", "File Exists", 0, 2);
                    if (option != 0) {
                        return;
                    }
                    if (!pluginFile.delete()) {
                        JOptionPane.showMessageDialog(this, "Unable to delete '" + pluginName + "'");
                        return;
                    }
                }
                this.pluginFile = pluginFile;
                (this.plugin = new Plugin(pluginFile)).setMaster(master);
                this.pluginNode = new PluginNode(this.plugin);
                try {
                    this.plugin.deleteVoiceFiles();
                }
                catch (IOException exc) {
                    Main.logException("I/O error while deleting old voice files", exc);
                }
                this.updateDisplay();
                return;
            }
            JOptionPane.showMessageDialog(this, "The plugin name may not contain a file path", "Name Not Valid", 0);
        }
    }
    
    private void openPlugin() {
        if (!this.closePlugin()) {
            return;
        }
        final File[] pluginFiles = PluginChooser.showDialog(this, PluginChooser.SELECT_BOTH_SINGLE);
        if (pluginFiles == null) {
            return;
        }
        final PluginNode pluginNode = CreateTreeTask.createTree(this, pluginFiles[0]);
        if (pluginNode != null) {
            this.pluginNode = pluginNode;
            this.plugin = pluginNode.getPlugin();
            this.pluginFile = this.plugin.getFile();
            this.updateDisplay();
        }
    }
    
    private boolean savePlugin() {
        this.searchNode = null;
        final int recordCount = this.plugin.getRecordCount();
        final boolean saved = SavePluginTask.savePlugin(this, this.pluginNode);
        if (saved) {
            Main.pluginModified = false;
            this.updateTitle();
            if (this.plugin.getRecordCount() != recordCount) {
                this.pluginTreeModel.nodeStructureChanged(this.pluginNode);
                this.countLabel.setText("Plugin record count: " + this.plugin.getRecordCount());
            }
        }
        return saved;
    }
    
    private boolean renamePlugin() {
        String pluginName = null;
        boolean master = false;
        while (true) {
            pluginName = JOptionPane.showInputDialog(this, "Enter the new name for the plugin");
            if (pluginName == null || pluginName.length() == 0) {
                return false;
            }
            if (pluginName.indexOf(47) < 0 && pluginName.indexOf(92) < 0) {
                final int sep = pluginName.lastIndexOf(46);
                if (sep < 0) {
                    pluginName = pluginName.concat(".esp");
                }
                else {
                    final String ext = pluginName.substring(sep);
                    if (ext.equalsIgnoreCase(".esm")) {
                        master = true;
                    }
                    else if (!ext.equalsIgnoreCase(".esp")) {
                        pluginName = pluginName.concat(".esp");
                    }
                }
                final File pluginFile = new File(Main.pluginPath + Main.fileSeparator + pluginName);
                if (pluginFile.exists()) {
                    final int option = JOptionPane.showConfirmDialog(this, "'" + pluginName + "' already exists.  Do you want to overwrite it?", "File Exists", 0, 2);
                    if (option != 0) {
                        return false;
                    }
                    if (!pluginFile.delete()) {
                        JOptionPane.showMessageDialog(this, "Unable to delete '" + pluginName + "'");
                        return false;
                    }
                }
                final String sourceName = this.plugin.getName();
                this.pluginFile = pluginFile;
                this.plugin.setFile(pluginFile);
                this.plugin.setMaster(master);
                this.pluginLabel.setText(this.plugin.getName());
                this.pluginTreeModel.nodeChanged(this.pluginNode);
                try {
                    this.plugin.copyVoiceFiles(sourceName);
                }
                catch (IOException exc) {
                    Main.logException("I/O error while copying voice files", exc);
                }
                catch (Throwable exc2) {
                    Main.logException("Exception while copying voice files", exc2);
                }
                return this.savePlugin();
            }
            JOptionPane.showMessageDialog(this, "The plugin name may not contain a file path", "Name Not Valid", 0);
        }
    }
    
    private boolean closePlugin() {
        if (this.plugin == null) {
            return true;
        }
        if (Main.pluginModified) {
            final int selection = JOptionPane.showConfirmDialog(this, "The current plugin has been modified. Do you want to save the changes?", "Plugin Modified", 0, 3);
            if (selection == 0) {
                final boolean saved = this.savePlugin();
                if (!saved) {
                    return false;
                }
            }
        }
        this.plugin = null;
        this.pluginFile = null;
        this.pluginNode = null;
        this.searchNode = null;
        Main.pluginModified = false;
        this.pluginLabel.setText(null);
        this.pluginTreeModel = new DefaultTreeModel(this.pluginNode);
        this.pluginTree.setModel(this.pluginTreeModel);
        this.masterTableModel = new DefaultTableModel(new String[0][2], this.masterColumns);
        this.masterTable.setModel(this.masterTableModel);
        this.countLabel.setText("Plugin record count: 0");
        this.updateTitle();
        return true;
    }
    
    private void mergePlugins() {
        final File[] mergePluginFiles = PluginChooser.showDialog(this, PluginChooser.SELECT_BOTH_MULTIPLE);
        if (mergePluginFiles == null) {
            return;
        }
        final PluginNode mergedNode = MergePluginTask.mergePlugin(this, this.plugin, mergePluginFiles);
        if (mergedNode != null) {
            Main.pluginModified = true;
            this.pluginNode = mergedNode;
            this.plugin = mergedNode.getPlugin();
            this.pluginFile = this.plugin.getFile();
            this.searchNode = null;
            this.updateDisplay();
        }
    }
    
    private void mergeLists() {
        if (this.plugin.isMaster()) {
            JOptionPane.showMessageDialog(this, "Lists cannot be merged into a master", "Master Not Allowed", 0);
            return;
        }
        final File[] mergePluginFiles = PluginChooser.showDialog(this, PluginChooser.SELECT_BOTH_MULTIPLE);
        if (mergePluginFiles == null) {
            return;
        }
        final PluginNode mergedNode = MergeListsTask.mergeLists(this, this.plugin, mergePluginFiles);
        if (mergedNode != null) {
            Main.pluginModified = true;
            this.pluginNode = mergedNode;
            this.plugin = mergedNode.getPlugin();
            this.pluginFile = this.plugin.getFile();
            this.searchNode = null;
            this.updateDisplay();
        }
    }
    
    private void editDescription() {
        if (EditDescriptionDialog.showDialog(this, this.plugin)) {
            Main.pluginModified = true;
            this.updateTitle();
        }
    }
    
    private void toggleMaster() {
        this.plugin.setMaster(!this.plugin.isMaster());
        this.pluginTreeModel.nodeChanged(this.pluginNode);
        Main.pluginModified = true;
        this.updateTitle();
    }
    
    private void toggleMasterList() {
        final int option = JOptionPane.showConfirmDialog(this, "Do you really want to change the master flag in each master list ESP?", "Toggle Master List", 0);
        if (option != 0) {
            return;
        }
        final List<MasterEntry> masterList = this.plugin.getMasterList();
        for (final MasterEntry master : masterList) {
            File file = null;
            RandomAccessFile inOut = null;
            long timestamp = 0L;
            final String name = master.getName();
            final int sep = name.lastIndexOf(46);
            if (sep <= 0) {
                continue;
            }
            final String extension = name.substring(sep);
            if (!extension.equalsIgnoreCase(".esp")) {
                continue;
            }
            try {
                file = new File(Main.pluginPath + Main.fileSeparator + name);
                timestamp = file.lastModified();
                inOut = new RandomAccessFile(file, "rw");
                final byte[] buffer = new byte[24];
                final int count = inOut.read(buffer);
                if (count != 24) {
                    throw new PluginException("Plugin header not found");
                }
                final String headerID = new String(buffer, 0, 4);
                if (!headerID.equals("TES4")) {
                    throw new PluginException("Plugin header not found");
                }
                if ((buffer[8] & 0x1) != 0x0) {
                    final byte[] array = buffer;
                    final int n = 8;
                    array[n] &= (byte)254;
                }
                else {
                    final byte[] array2 = buffer;
                    final int n2 = 8;
                    array2[n2] |= 0x1;
                }
                inOut.seek(8L);
                inOut.write(buffer, 8, 1);
                inOut.close();
                inOut = null;
                continue;
            }
            catch (PluginException exc) {
                Main.logException(name + " is not a valid plugin", exc);
            }
            catch (IOException exc2) {
                Main.logException("I/O error while processing " + name, exc2);
            }
            catch (Throwable exc3) {
                Main.logException("Exception while processing " + name, exc3);
            }
            finally {
                if (inOut != null) {
                    try {
                        inOut.close();
                    }
                    catch (IOException exc4) {
                        Main.logException("I/O error while closing " + name, exc4);
                    }
                }
                else if (file != null && timestamp != 0L) {
                    file.setLastModified(timestamp);
                }
                inOut = null;
                file = null;
                timestamp = 0L;
            }
        }
    }
    
    private void toggleIgnore() {
        final TreePath[] treePaths = this.pluginTree.getSelectionPaths();
        if (treePaths == null) {
            JOptionPane.showMessageDialog(this, "You must select at least one record or group to process", "Error", 0);
            return;
        }
        for (final TreePath treePath : treePaths) {
            final DefaultMutableTreeNode node = (DefaultMutableTreeNode)treePath.getLastPathComponent();
            if (!(node instanceof RecordNode) && !(node instanceof GroupNode)) {
                JOptionPane.showMessageDialog(this, "Only records and groups may be selected", "Error", 0);
                return;
            }
        }
        for (final TreePath treePath : treePaths) {
            final DefaultMutableTreeNode node = (DefaultMutableTreeNode)treePath.getLastPathComponent();
            if (node instanceof GroupNode) {
                this.toggleGroupIgnore((GroupNode)node);
            }
            else {
                this.toggleRecordIgnore((RecordNode)node);
            }
        }
        this.updateTitle();
    }
    
    private void toggleGroupIgnore(final GroupNode groupNode) {
        for (int count = groupNode.getChildCount(), index = 0; index < count; ++index) {
            final DefaultMutableTreeNode node = (DefaultMutableTreeNode)groupNode.getChildAt(index);
            if (node instanceof GroupNode) {
                this.toggleGroupIgnore((GroupNode)node);
            }
            else {
                this.toggleRecordIgnore((RecordNode)node);
            }
        }
    }
    
    private void toggleRecordIgnore(final RecordNode recordNode) {
        final PluginRecord record = recordNode.getRecord();
        if (record.isIgnored()) {
            record.setIgnore(false);
        }
        else {
            record.setIgnore(true);
        }
        this.pluginTreeModel.nodeChanged(recordNode);
        Main.pluginModified = true;
    }
    
    private void displaySubrecordData() {
        final TreePath[] treePaths = this.pluginTree.getSelectionPaths();
        if (treePaths == null) {
            JOptionPane.showMessageDialog(this, "You must select at least one subrecord to display", "Error", 0);
            return;
        }
        for (final TreePath treePath : treePaths) {
            final DefaultMutableTreeNode node = (DefaultMutableTreeNode)treePath.getLastPathComponent();
            if (!(node instanceof SubrecordNode)) {
                JOptionPane.showMessageDialog(this, "Only subrecords may be displayed", "Error", 0);
                return;
            }
        }
        for (final TreePath treePath : treePaths) {
            final SubrecordNode node2 = (SubrecordNode)treePath.getLastPathComponent();
            DisplaySubrecordDialog.showDialog(this, node2.getSubrecord());
        }
    }
    
    private void findFormID() {
        final String text = this.formField.getText();
        if (text == null || text.length() == 0) {
            JOptionPane.showMessageDialog(this, "You must enter a search term", "Enter search term", 0);
            return;
        }
        Integer objFormID = null;
        PluginRecord record = null;
        try {
            final int formID = Integer.parseInt(text, 16);
            objFormID = new Integer(formID);
            record = this.plugin.getFormIDMap().get(objFormID);
        }
        catch (NumberFormatException ex) {}
        if (record == null) {
            JOptionPane.showMessageDialog(this, "No match found for '" + text + "'", "No match found", 0);
        }
        else {
            this.pluginTree.clearSelection();
            final RecordNode recordNode = this.pluginNode.getRecordMap().get(objFormID);
            final TreePath treePath = new TreePath(recordNode.getPath());
            this.pluginTree.setSelectionPath(treePath);
            this.pluginTree.scrollPathToVisible(treePath);
        }
    }
    
    private void findEditorID(final boolean resume) {
        if (!resume) {
            this.searchNode = null;
        }
        final String text = this.searchField.getText();
        if (text == null || text.length() == 0) {
            JOptionPane.showMessageDialog(this, "You must enter a search term", "Enter search term", 0);
            return;
        }
        Pattern p = null;
        try {
            p = Pattern.compile(text, 2);
        }
        catch (PatternSyntaxException exc) {
            JOptionPane.showMessageDialog(this, "'" + text + "' is not a valid regular expression", "Invalid regular expression", 0);
        }
        if (p == null) {
            return;
        }
        boolean foundMatch = false;
        DefaultMutableTreeNode groupNode = null;
        int searchIndex = -1;
        if (this.searchNode != null) {
            groupNode = (DefaultMutableTreeNode)this.searchNode.getParent();
            searchIndex = groupNode.getIndex(this.searchNode);
        }
        else if (this.pluginNode.getChildCount() > 0) {
            groupNode = (DefaultMutableTreeNode)this.pluginNode.getFirstChild();
            searchIndex = -1;
        }
        while (!foundMatch && groupNode != null) {
            if (++searchIndex < groupNode.getChildCount()) {
                this.searchNode = (DefaultMutableTreeNode)groupNode.getChildAt(searchIndex);
                if (this.searchNode instanceof GroupNode) {
                    groupNode = this.searchNode;
                    searchIndex = -1;
                }
                else {
                    if (!(this.searchNode instanceof RecordNode)) {
                        continue;
                    }
                    final PluginRecord searchRecord = ((RecordNode)this.searchNode).getRecord();
                    final Matcher m = p.matcher(searchRecord.getEditorID());
                    if (!m.matches()) {
                        continue;
                    }
                    foundMatch = true;
                }
            }
            else {
                this.searchNode = groupNode;
                groupNode = (DefaultMutableTreeNode)groupNode.getParent();
                if (groupNode == null) {
                    continue;
                }
                searchIndex = groupNode.getIndex(this.searchNode);
            }
        }
        if (!foundMatch) {
            this.searchNode = null;
            JOptionPane.showMessageDialog(this, "No match found for '" + text + "'", "No match found", 0);
        }
        else {
            this.pluginTree.clearSelection();
            final TreePath treePath = new TreePath(this.searchNode.getPath());
            this.pluginTree.setSelectionPath(treePath);
            this.pluginTree.scrollPathToVisible(treePath);
        }
    }
    
    private void exitProgram() {
        this.closePlugin();
        if (this.windowListener.getWindowState() == 0) {
            final Point p = Main.mainWindow.getLocation();
            final Dimension d = Main.mainWindow.getSize();
            Main.properties.setProperty("window.main.position", p.x + "," + p.y);
            Main.properties.setProperty("window.main.size", d.width + "," + d.height);
        }
        Main.saveProperties();
        System.exit(0);
    }
    
    private void aboutProgram() {
        final StringBuilder info = new StringBuilder(256);
        info.append("<html>Fallout New Vegas Plugin Utility Version 1.7<br>");
        info.append("<br>User name: ");
        info.append(System.getProperty("user.name"));
        info.append("<br>Home directory: ");
        info.append(System.getProperty("user.home"));
        info.append("<br>Work directory: ");
        info.append(Main.tmpDir);
        info.append("<br>Plugin directory: ");
        info.append(Main.pluginPath);
        info.append("<br><br>OS: ");
        info.append(System.getProperty("os.name"));
        info.append("<br>OS version: ");
        info.append(System.getProperty("os.version"));
        info.append("<br><br>Java vendor: ");
        info.append(System.getProperty("java.vendor"));
        info.append("<br>Java version: ");
        info.append(System.getProperty("java.version"));
        info.append("<br>Java home directory: ");
        info.append(System.getProperty("java.home"));
        info.append("<br>Java class path: ");
        info.append(System.getProperty("java.class.path"));
        info.append("</html>");
        JOptionPane.showMessageDialog(this, info.toString(), "About Fallout 3 Plugin Utility", 1);
    }
    
    private class ApplicationWindowListener extends WindowAdapter
    {
        private int windowState;
        
        public ApplicationWindowListener() {
            this.windowState = 0;
        }
        
        public int getWindowState() {
            return this.windowState;
        }
        
        @Override
        public void windowStateChanged(final WindowEvent we) {
            this.windowState = we.getNewState();
        }
        
        @Override
        public void windowClosing(final WindowEvent we) {
            try {
                MainWindow.this.exitProgram();
            }
            catch (Exception exc) {
                Main.logException("Exception while closing application window", exc);
            }
        }
    }
}
