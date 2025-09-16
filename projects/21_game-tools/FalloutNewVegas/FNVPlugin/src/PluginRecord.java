// 
// Decompiled by Procyon v0.5.36
// 

package FNVPlugin;

import java.util.zip.Deflater;
import java.util.Iterator;
import java.util.ListIterator;
import java.io.IOException;
import java.util.zip.DataFormatException;
import java.util.zip.Inflater;
import java.io.EOFException;
import java.io.RandomAccessFile;
import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class PluginRecord extends SerializedElement
{
    private static final String dummyString;
    private String recordType;
    private int recordFlags;
    private byte[] timestamp;
    private int formVersion;
    private int formID;
    private String editorID;
    private String fullName;
    private List<PluginSubrecord> subrecordList;
    
    public PluginRecord(final SerializedElement parent, final String recordType, final int formID) {
        super(parent);
        this.recordType = recordType;
        this.formID = formID;
        this.editorID = PluginRecord.dummyString;
        this.fullName = PluginRecord.dummyString;
        this.timestamp = new byte[4];
        this.formVersion = 15;
        this.subrecordList = new ArrayList<PluginSubrecord>(10);
    }
    
    public PluginRecord(final SerializedElement parent, final File file, final RandomAccessFile in, final byte[] prefix) throws DataFormatException, IOException, PluginException {
        super(parent);
        if (prefix.length != 24) {
            throw new IllegalArgumentException("The record prefix is not 24 bytes");
        }
        this.editorID = PluginRecord.dummyString;
        this.fullName = PluginRecord.dummyString;
        this.timestamp = new byte[4];
        this.subrecordList = new ArrayList<PluginSubrecord>(10);
        this.recordType = new String(prefix, 0, 4);
        final int recordLength = SerializedElement.getInteger(prefix, 4);
        this.recordFlags = SerializedElement.getInteger(prefix, 8);
        this.formID = SerializedElement.getInteger(prefix, 12);
        System.arraycopy(prefix, 16, this.timestamp, 0, 4);
        this.formVersion = SerializedElement.getInteger(prefix, 20);
        int offset = 0;
        int overrideLength = 0;
        final byte[] recordData = new byte[recordLength];
        int count = in.read(recordData);
        if (count != recordLength) {
            throw new EOFException(file.getName() + ": " + this.recordType + " record is incomplete");
        }
        int dataLength;
        byte[] buffer;
        if (this.isCompressed()) {
            if (recordLength < 5 || recordData[3] >= 32) {
                throw new PluginException("Compressed data prefix is not valid");
            }
            dataLength = SerializedElement.getInteger(recordData, 0);
            buffer = new byte[dataLength];
            final Inflater expand = new Inflater();
            expand.setInput(recordData, 4, recordLength - 4);
            try {
                count = expand.inflate(buffer);
            }
            catch (DataFormatException exc) {
                final String errorMsg = String.format("Unable to decompress %s record %08X - Subrecords discarded", this.recordType, this.formID);
                Main.logException(errorMsg, exc);
                dataLength = 0;
                count = 0;
            }
            if (count != dataLength) {
                throw new PluginException("Expanded data does not match the data length");
            }
            expand.end();
        }
        else {
            dataLength = recordLength;
            buffer = recordData;
        }
        while (dataLength >= 6) {
            final String subrecordType = new String(buffer, offset, 4);
            int length = SerializedElement.getShort(buffer, offset + 4);
            if (length == 0) {
                length = overrideLength;
                overrideLength = 0;
            }
            offset += 6;
            dataLength -= 6;
            if (length > dataLength) {
                throw new PluginException(file.getName() + ": " + subrecordType + " subrecord is incomplete");
            }
            if (subrecordType.equals("XXXX")) {
                if (length != 4) {
                    throw new PluginException(file.getName() + ": XXXX subrecord data length is not 4");
                }
                overrideLength = SerializedElement.getInteger(buffer, offset);
            }
            else {
                final byte[] subrecordData = new byte[length];
                if (length > 0) {
                    System.arraycopy(buffer, offset, subrecordData, 0, length);
                }
                final PluginSubrecord subrecord = new PluginSubrecord(this, subrecordType, subrecordData);
                this.subrecordList.add(subrecord);
                if (subrecordType.equals("EDID") && length > 1) {
                    this.editorID = new String(subrecordData, 0, length - 1);
                }
                else if (subrecordType.equals("FULL") && length > 1) {
                    this.fullName = new String(subrecordData, 0, length - 1);
                }
            }
            offset += length;
            dataLength -= length;
        }
        if (dataLength != 0) {
            throw new PluginException(file.getName() + ": " + this.recordType + " record data is incomplete");
        }
    }
    
    public boolean isDeleted() {
        return (this.recordFlags & 0x20) != 0x0;
    }
    
    public void setDelete(final boolean deleted) {
        if (deleted) {
            this.recordFlags |= 0x20;
        }
        else {
            this.recordFlags &= 0xFFFFFFDF;
        }
    }
    
    public boolean isIgnored() {
        return (this.recordFlags & 0x1000) != 0x0;
    }
    
    public void setIgnore(final boolean ignored) {
        if (ignored) {
            this.recordFlags |= 0x1000;
        }
        else {
            this.recordFlags &= 0xFFFFEFFF;
        }
    }
    
    public boolean isCompressed() {
        return (this.recordFlags & 0x40000) != 0x0;
    }
    
    public String getRecordType() {
        return this.recordType;
    }
    
    public int getRecordFlags() {
        return this.recordFlags;
    }
    
    public void setRecordFlags(final int recordFlags) {
        this.recordFlags = recordFlags;
    }
    
    public int getFormID() {
        return this.formID;
    }
    
    public void setFormID(final int formID) {
        this.formID = formID;
    }
    
    public String getEditorID() {
        return this.editorID;
    }
    
    public void setEditorID(final String editorID) {
        if (this.editorID.equals(editorID)) {
            return;
        }
        this.editorID = editorID;
        final ListIterator<PluginSubrecord> lit = this.subrecordList.listIterator();
        while (lit.hasNext()) {
            final PluginSubrecord subrecord = lit.next();
            if (subrecord.getSubrecordType().equals("EDID")) {
                lit.remove();
                break;
            }
        }
        final byte[] edidData = editorID.getBytes();
        final byte[] subrecordData = new byte[edidData.length + 1];
        System.arraycopy(edidData, 0, subrecordData, 0, edidData.length);
        subrecordData[edidData.length] = 0;
        final PluginSubrecord edidSubrecord = new PluginSubrecord(this, "EDID", subrecordData);
        this.subrecordList.add(0, edidSubrecord);
    }
    
    public String getFullName() {
        return this.fullName;
    }
    
    public List<PluginSubrecord> getSubrecords() {
        return this.subrecordList;
    }
    
    public void changeFormID(final int newFormID) {
        final PluginGroup parentGroup = (PluginGroup)this.getParent();
        if (parentGroup != null) {
            final List<SerializedElement> parentRecordList = parentGroup.getRecordList();
            final int index = parentRecordList.indexOf(this);
            if (index >= 0 && index < parentRecordList.size() - 1) {
                final SerializedElement checkElement = parentRecordList.get(index + 1);
                if (checkElement instanceof PluginGroup) {
                    final PluginGroup checkGroup = (PluginGroup)checkElement;
                    if (checkGroup.getGroupParentID() == this.formID) {
                        checkGroup.setGroupParentID(newFormID);
                        final List<SerializedElement> subgroupRecordList = checkGroup.getRecordList();
                        for (final SerializedElement subgroupElement : subgroupRecordList) {
                            if (subgroupElement instanceof PluginGroup) {
                                final PluginGroup checkSubgroup = (PluginGroup)subgroupElement;
                                if (checkSubgroup.getGroupParentID() != this.formID) {
                                    continue;
                                }
                                checkSubgroup.setGroupParentID(newFormID);
                            }
                        }
                    }
                }
            }
        }
        this.formID = newFormID;
    }
    
    public boolean updateReferences(final FormAdjust formAdjust) {
        boolean recordModified = false;
        for (final PluginSubrecord subrecord : this.subrecordList) {
            final byte[] subrecordData = subrecord.getSubrecordData();
            final int[][] references = subrecord.getReferences();
            if (references == null) {
                continue;
            }
            for (int i = 0; i < references.length; ++i) {
                final int offset = references[i][0];
                final int oldFormID = references[i][1];
                if (oldFormID != 0) {
                    final int newFormID = formAdjust.adjustFormID(oldFormID);
                    if (newFormID != oldFormID) {
                        SerializedElement.setInteger(newFormID, subrecordData, offset);
                        recordModified = true;
                    }
                }
            }
        }
        return recordModified;
    }
    
    public void store(final RandomAccessFile out) throws DataFormatException, IOException {
        int recordLength = 0;
        for (final PluginSubrecord subrecord : this.subrecordList) {
            final int subrecordLength = subrecord.getSubrecordData().length;
            recordLength += 6 + subrecordLength;
            if (subrecordLength > 65535) {
                recordLength += 10;
            }
        }
        byte[] recordData = new byte[recordLength];
        int offset = 0;
        for (final PluginSubrecord subrecord2 : this.subrecordList) {
            final byte[] subrecordData = subrecord2.getSubrecordData();
            final int subrecordLength2 = subrecordData.length;
            if (subrecordLength2 > 65535) {
                System.arraycopy("XXXX".getBytes(), 0, recordData, offset, 4);
                SerializedElement.setShort(4, recordData, offset + 4);
                SerializedElement.setInteger(subrecordLength2, recordData, offset + 6);
                offset += 10;
            }
            System.arraycopy(subrecord2.getSubrecordType().getBytes(), 0, recordData, offset, 4);
            if (subrecordLength2 > 65535) {
                SerializedElement.setShort(0, recordData, offset + 4);
            }
            else {
                SerializedElement.setShort(subrecordLength2, recordData, offset + 4);
            }
            if (subrecordLength2 > 0) {
                System.arraycopy(subrecordData, 0, recordData, offset + 6, subrecordLength2);
            }
            offset += 6 + subrecordLength2;
        }
        if (this.isCompressed()) {
            final Deflater comp = new Deflater(6);
            comp.setInput(recordData);
            comp.finish();
            final byte[] compBuffer = new byte[recordLength + 20];
            final int compLength = comp.deflate(compBuffer);
            if (compLength == 0) {
                throw new DataFormatException("Unable to compress " + this.recordType + " record " + this.editorID);
            }
            if (!comp.finished()) {
                throw new DataFormatException("Compressed buffer is too small");
            }
            comp.end();
            recordData = new byte[4 + compLength];
            SerializedElement.setInteger(recordLength, recordData, 0);
            System.arraycopy(compBuffer, 0, recordData, 4, compLength);
            recordLength = recordData.length;
        }
        final byte[] prefix = new byte[24];
        System.arraycopy(this.recordType.getBytes(), 0, prefix, 0, 4);
        SerializedElement.setInteger(recordLength, prefix, 4);
        SerializedElement.setInteger(this.recordFlags, prefix, 8);
        SerializedElement.setInteger(this.formID, prefix, 12);
        System.arraycopy(this.timestamp, 0, prefix, 16, 4);
        SerializedElement.setInteger(this.formVersion, prefix, 20);
        out.write(prefix);
        if (recordLength != 0) {
            out.write(recordData);
        }
    }
    
    @Override
    public int hashCode() {
        return this.formID;
    }
    
    @Override
    public boolean equals(final Object object) {
        boolean areEqual = false;
        if (object instanceof PluginRecord) {
            final PluginRecord objRecord = (PluginRecord)object;
            if (objRecord.getRecordType().equals(this.recordType)) {
                if (this.recordType.equals("GMST")) {
                    if (objRecord.getEditorID().equalsIgnoreCase(this.editorID)) {
                        areEqual = true;
                    }
                }
                else if (objRecord.getFormID() == this.formID) {
                    areEqual = true;
                }
            }
        }
        return areEqual;
    }
    
    @Override
    public String toString() {
        String text = String.format("%s record: %s (%08X)", this.recordType, this.editorID, this.formID);
        if (this.fullName.length() > 0) {
            text = text + " - " + this.fullName;
        }
        if (this.isIgnored()) {
            text = "(Ignore) " + text;
        }
        else if (this.isDeleted()) {
            text = "(Deleted) " + text;
        }
        return text;
    }
    
    @Override
    public Object clone() {
        final Object clonedObject = super.clone();
        final PluginRecord clonedRecord = (PluginRecord)clonedObject;
        clonedRecord.timestamp = new byte[4];
        System.arraycopy(this.timestamp, 0, clonedRecord.timestamp, 0, 4);
        clonedRecord.subrecordList = new ArrayList<PluginSubrecord>(this.subrecordList.size());
        for (final PluginSubrecord subrecord : this.subrecordList) {
            final PluginSubrecord clonedSubrecord = (PluginSubrecord)subrecord.clone();
            clonedSubrecord.setParent(clonedRecord);
            clonedRecord.subrecordList.add(clonedSubrecord);
        }
        return clonedObject;
    }
    
    static {
        dummyString = new String();
    }
}
