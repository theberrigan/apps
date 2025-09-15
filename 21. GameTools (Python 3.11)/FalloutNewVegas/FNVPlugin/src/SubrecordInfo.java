// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

public class SubrecordInfo
{
    private SubrecordInfo subrecordChain;
    private String subrecordType;
    private String[] recordTypes;
    private int[] referenceOffsets;
    
    public SubrecordInfo(final String subrecordType, final int[] referenceOffsets, final String... recordTypes) {
        this.subrecordType = subrecordType;
        this.referenceOffsets = referenceOffsets;
        this.recordTypes = new String[recordTypes.length];
        for (int i = 0; i < recordTypes.length; ++i) {
            this.recordTypes[i] = recordTypes[i];
        }
    }
    
    public String getSubrecordType() {
        return this.subrecordType;
    }
    
    public String[] getRecordTypes() {
        return this.recordTypes;
    }
    
    public int[] getReferenceOffsets() {
        return this.referenceOffsets;
    }
    
    public SubrecordInfo getSubrecordChain() {
        return this.subrecordChain;
    }
    
    public void setSubrecordChain(final SubrecordInfo subrecordChain) {
        this.subrecordChain = subrecordChain;
    }
}
