// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import java.util.Iterator;
import java.util.ArrayList;
import java.util.List;

public class MasterEntry implements Cloneable
{
    private String masterName;
    private List<Integer> masterOverrides;
    
    public MasterEntry(final String masterName) {
        this.masterName = masterName;
        this.masterOverrides = new ArrayList<Integer>();
    }
    
    public String getName() {
        return this.masterName;
    }
    
    public List<Integer> getOverrides() {
        return this.masterOverrides;
    }
    
    @Override
    public boolean equals(final Object object) {
        boolean areEqual = false;
        if (object instanceof MasterEntry && ((MasterEntry)object).getName().equalsIgnoreCase(this.masterName)) {
            areEqual = true;
        }
        return areEqual;
    }
    
    @Override
    public String toString() {
        return this.masterName;
    }
    
    public Object clone() {
        Object clonedObject = null;
        try {
            clonedObject = super.clone();
            final MasterEntry clonedEntry = (MasterEntry)clonedObject;
            clonedEntry.masterOverrides = new ArrayList<Integer>(this.masterOverrides.size());
            for (final Integer override : this.masterOverrides) {
                clonedEntry.masterOverrides.add(override);
            }
        }
        catch (CloneNotSupportedException exc) {
            throw new UnsupportedOperationException("Unable to clone master entry", exc);
        }
        return clonedObject;
    }
}
