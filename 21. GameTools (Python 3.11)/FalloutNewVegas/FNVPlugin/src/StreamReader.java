// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import java.io.IOException;
import java.io.InputStream;
import java.io.StringWriter;
import java.io.InputStreamReader;

public class StreamReader extends Thread
{
    private InputStreamReader reader;
    private StringWriter writer;
    private StringBuffer buffer;
    private int index;
    
    public StreamReader(final InputStream inputStream) {
        this.index = 0;
        this.reader = new InputStreamReader(inputStream);
        this.writer = new StringWriter(1024);
    }
    
    @Override
    public void run() {
        try {
            int c;
            while ((c = this.reader.read()) != -1) {
                this.writer.write(c);
            }
            this.reader.close();
            this.buffer = this.writer.getBuffer();
        }
        catch (IOException exc) {
            Main.logException("Unable to read from input stream", exc);
        }
    }
    
    public StringBuffer getBuffer() throws IllegalThreadStateException {
        if (this.buffer == null) {
            throw new IllegalThreadStateException("Input stream is still open");
        }
        return this.buffer;
    }
    
    public String getLine() throws IllegalThreadStateException {
        if (this.buffer == null) {
            throw new IllegalThreadStateException("Input stream is still open");
        }
        String line = null;
        final int length = this.buffer.length();
        if (this.index < length) {
            final int sep = this.buffer.indexOf(Main.lineSeparator, this.index);
            if (sep < 0) {
                line = this.buffer.substring(this.index);
                this.index = length;
            }
            else {
                line = this.buffer.substring(this.index, sep);
                this.index = sep + Main.lineSeparator.length();
            }
        }
        return line;
    }
}
