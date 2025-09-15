// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

public class SerializedElement implements Cloneable
{
    private SerializedElement parent;
    
    public SerializedElement() {
    }
    
    public SerializedElement(final SerializedElement parent) {
        this.parent = parent;
    }
    
    public SerializedElement getParent() {
        return this.parent;
    }
    
    public void setParent(final SerializedElement parent) {
        this.parent = parent;
    }
    
    public static int compareArrays(final byte[] arrayA, final int positionA, final byte[] arrayB, final int positionB, final int count) {
        int diff = 0;
        int indexA = positionA;
        int indexB = positionB;
        int i = 0;
        while (i < count) {
            if (arrayA[indexA] != arrayB[indexB]) {
                if ((arrayA[indexA] & 0xFF) > (arrayB[indexB] & 0xFF)) {
                    diff = 1;
                    break;
                }
                diff = -1;
                break;
            }
            else {
                ++indexA;
                ++indexB;
                ++i;
            }
        }
        return diff;
    }
    
    public static int getShort(final byte[] buffer, final int offset) {
        return (buffer[offset + 0] & 0xFF) | (buffer[offset + 1] & 0xFF) << 8;
    }
    
    public static void setShort(final int number, final byte[] buffer, final int offset) {
        buffer[offset] = (byte)number;
        buffer[offset + 1] = (byte)(number >>> 8);
    }
    
    public static int getInteger(final byte[] buffer, final int offset) {
        return (buffer[offset + 0] & 0xFF) | (buffer[offset + 1] & 0xFF) << 8 | (buffer[offset + 2] & 0xFF) << 16 | (buffer[offset + 3] & 0xFF) << 24;
    }
    
    public static void setInteger(final int number, final byte[] buffer, final int offset) {
        buffer[offset] = (byte)number;
        buffer[offset + 1] = (byte)(number >>> 8);
        buffer[offset + 2] = (byte)(number >>> 16);
        buffer[offset + 3] = (byte)(number >>> 24);
    }
    
    public static long getLong(final byte[] buffer, final int offset) {
        return ((long)buffer[offset + 0] & 0xFFL) | ((long)buffer[offset + 1] & 0xFFL) << 8 | ((long)buffer[offset + 2] & 0xFFL) << 16 | ((long)buffer[offset + 3] & 0xFFL) << 24 | ((long)buffer[offset + 4] & 0xFFL) << 32 | ((long)buffer[offset + 5] & 0xFFL) << 40 | ((long)buffer[offset + 6] & 0xFFL) << 48 | ((long)buffer[offset + 7] & 0xFFL) << 56;
    }
    
    public static void setLong(final long number, final byte[] buffer, final int offset) {
        buffer[offset] = (byte)number;
        buffer[offset + 1] = (byte)(number >>> 8);
        buffer[offset + 2] = (byte)(number >>> 16);
        buffer[offset + 3] = (byte)(number >>> 24);
        buffer[offset + 4] = (byte)(number >>> 32);
        buffer[offset + 5] = (byte)(number >>> 40);
        buffer[offset + 6] = (byte)(number >>> 48);
        buffer[offset + 7] = (byte)(number >>> 56);
    }
    
    public Object clone() {
        Object clonedObject = null;
        try {
            clonedObject = super.clone();
        }
        catch (CloneNotSupportedException exc) {
            throw new UnsupportedOperationException("Unable to clone element", exc);
        }
        return clonedObject;
    }
}
