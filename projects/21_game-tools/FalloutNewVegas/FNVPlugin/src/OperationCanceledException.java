// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

public class OperationCanceledException extends Exception
{
    public OperationCanceledException() {
    }
    
    public OperationCanceledException(final String exceptionMsg) {
        super(exceptionMsg);
    }
    
    public OperationCanceledException(final String exceptionMsg, final Throwable cause) {
        super(exceptionMsg, cause);
    }
}
