// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

public class FunctionInfo
{
    private String functionName;
    private int functionCode;
    private boolean firstReference;
    private boolean secondReference;
    
    public FunctionInfo(final String name, final int code, final boolean firstParam, final boolean secondParam) {
        this.functionName = name;
        this.functionCode = code;
        this.firstReference = firstParam;
        this.secondReference = secondParam;
    }
    
    public String getName() {
        return this.functionName;
    }
    
    public int getCode() {
        return this.functionCode;
    }
    
    public boolean isFirstReference() {
        return this.firstReference;
    }
    
    public boolean isSecondReference() {
        return this.secondReference;
    }
}
