// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import java.io.OutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import javax.swing.JOptionPane;
import java.awt.Component;
import javax.swing.JFileChooser;
import javax.swing.SwingUtilities;
import javax.swing.UIManager;
import java.io.InputStream;
import java.io.FileInputStream;
import java.util.Properties;
import java.io.File;
import javax.swing.JFrame;

public class Main
{
    public static String fileSeparator;
    public static String lineSeparator;
    public static String pluginPath;
    public static boolean pluginModified;
    public static String tmpDir;
    public static JFrame mainWindow;
    public static File propFile;
    public static Properties properties;
    public static boolean debugMode;
    private static String deferredText;
    private static Throwable deferredException;
    
    public static void main(final String[] args) {
        try {
            Main.lineSeparator = System.getProperty("line.separator");
            Main.fileSeparator = System.getProperty("file.separator");
            Main.tmpDir = new File(System.getProperty("java.io.tmpdir")).getCanonicalPath();
            final String debugString = System.getProperty("debug.plugin");
            if (debugString != null && debugString.equals("1")) {
                Main.debugMode = true;
            }
            String filePath = System.getProperty("user.home") + Main.fileSeparator + "Application Data" + Main.fileSeparator + "ScripterRon";
            final File dirFile = new File(filePath);
            if (!dirFile.exists()) {
                dirFile.mkdirs();
            }
            filePath = filePath + Main.fileSeparator + "FNVPlugin.properties";
            Main.propFile = new File(filePath);
            Main.properties = new Properties();
            if (Main.propFile.exists()) {
                final FileInputStream in = new FileInputStream(Main.propFile);
                Main.properties.load(in);
                in.close();
            }
            Main.pluginPath = System.getProperty("Fallout.plugin.path");
            if (Main.pluginPath == null) {
                Main.pluginPath = Main.properties.getProperty("Fallout.plugin.path");
                if (Main.pluginPath == null) {
                    String installPath = null;
                    final String regString = "reg query \"HKLM\\Software\\Bethesda Softworks\\FalloutNV\" /v \"Installed Path\"";
                    final Process process = Runtime.getRuntime().exec(regString);
                    final StreamReader streamReader = new StreamReader(process.getInputStream());
                    streamReader.start();
                    process.waitFor();
                    streamReader.join();
                    String line;
                    while ((line = streamReader.getLine()) != null) {
                        final int sep = line.indexOf("REG_SZ");
                        if (sep >= 0) {
                            installPath = line.substring(sep + 6).trim();
                            break;
                        }
                    }
                    if (installPath != null) {
                        if (installPath.charAt(installPath.length() - 1) != '\\') {
                            Main.pluginPath = installPath + Main.fileSeparator + "Data";
                        }
                        else {
                            Main.pluginPath = installPath + "Data";
                        }
                    }
                }
            }
            Main.properties.setProperty("java.version", System.getProperty("java.version"));
            Main.properties.setProperty("java.home", System.getProperty("java.home"));
            Main.properties.setProperty("os.name", System.getProperty("os.name"));
            Main.properties.setProperty("user.name", System.getProperty("user.name"));
            Main.properties.setProperty("user.home", System.getProperty("user.home"));
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
            SwingUtilities.invokeLater(new Runnable() {
                @Override
                public void run() {
                    Main.createAndShowGUI();
                }
            });
        }
        catch (Exception exc) {
            logException("Exception during program initialization", exc);
        }
    }
    
    public static void createAndShowGUI() {
        try {
            JFrame.setDefaultLookAndFeelDecorated(true);
            while (true) {
                File dirPath = null;
                if (Main.pluginPath == null) {
                    try {
                        final JFileChooser chooser = new JFileChooser();
                        chooser.setDialogTitle("Select Plugin Directory");
                        chooser.setApproveButtonText("Select");
                        chooser.setFileSelectionMode(1);
                        if (chooser.showOpenDialog(Main.mainWindow) == 0) {
                            dirPath = chooser.getSelectedFile();
                            Main.pluginPath = dirPath.getPath();
                        }
                    }
                    catch (Exception exc2) {
                        Main.pluginPath = JOptionPane.showInputDialog(Main.mainWindow, "Enter the fully-qualified path for the plugin directory.", "Enter Plugin Directory", 1);
                        if (Main.pluginPath != null) {
                            dirPath = new File(Main.pluginPath);
                        }
                    }
                    if (Main.pluginPath == null) {
                        throw new IOException("Unable to locate Fallout plugin directory");
                    }
                }
                else {
                    dirPath = new File(Main.pluginPath);
                }
                if (!dirPath.exists()) {
                    JOptionPane.showMessageDialog(Main.mainWindow, "\"" + Main.pluginPath + "\" does not exist", "Plugin path is not valid", 0);
                    Main.pluginPath = null;
                }
                else {
                    if (dirPath.isDirectory()) {
                        Main.properties.setProperty("Fallout.plugin.path", Main.pluginPath);
                        (Main.mainWindow = new MainWindow()).pack();
                        Main.mainWindow.setVisible(true);
                        break;
                    }
                    JOptionPane.showMessageDialog(Main.mainWindow, "\"" + Main.pluginPath + "\" is not a directory", "Plugin path is not valid", 0);
                    Main.pluginPath = null;
                }
            }
        }
        catch (Throwable exc) {
            logException("Exception while initializing application window", exc);
        }
    }
    
    public static void saveProperties() {
        try {
            final FileOutputStream out = new FileOutputStream(Main.propFile);
            Main.properties.store(out, "FNVPlugin Properties");
            out.close();
        }
        catch (Throwable exc) {
            logException("Exception while saving application properties", exc);
        }
    }
    
    public static void logException(final String text, final Throwable exc) {
        System.runFinalization();
        System.gc();
        if (SwingUtilities.isEventDispatchThread()) {
            final StringBuilder string = new StringBuilder(512);
            string.append("<html><b>");
            string.append(text);
            string.append("</b><br><br>");
            string.append(exc.toString());
            string.append("<br>");
            final StackTraceElement[] trace = exc.getStackTrace();
            int count = 0;
            for (final StackTraceElement elem : trace) {
                string.append(elem.toString());
                string.append("<br>");
                if (++count == 25) {
                    break;
                }
            }
            string.append("</html>");
            JOptionPane.showMessageDialog(Main.mainWindow, string, "Error", 0);
        }
        else if (Main.deferredException == null) {
            Main.deferredText = text;
            Main.deferredException = exc;
            try {
                SwingUtilities.invokeAndWait(new Runnable() {
                    @Override
                    public void run() {
                        Main.logException(Main.deferredText, Main.deferredException);
                        Main.deferredException = null;
                        Main.deferredText = null;
                    }
                });
            }
            catch (Throwable swingException) {
                Main.deferredException = null;
                Main.deferredText = null;
            }
        }
    }
    
    public static void dumpData(final String text, final byte[] data, final int length) {
        System.out.println(text);
        for (int i = 0; i < length; ++i) {
            if (i % 32 == 0) {
                System.out.print(String.format(" %14X  ", i));
            }
            else if (i % 4 == 0) {
                System.out.print(" ");
            }
            System.out.print(String.format("%02X", data[i]));
            if (i % 32 == 31) {
                System.out.println();
            }
        }
        if (length % 32 != 0) {
            System.out.println();
        }
    }
    
    static {
        Main.pluginModified = false;
        Main.debugMode = false;
    }
}
