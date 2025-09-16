import {IsLicensePlateExpiredPipe} from './is-license-plate-expired.pipe';
import {LicensePlateItem} from "../../../../../services/license-plates.service";// Adjust the import according to your file structure

describe('IsLicensePlateExpiredPipe', () => {
    let pipe: IsLicensePlateExpiredPipe;

    beforeEach(() => {
        pipe = new IsLicensePlateExpiredPipe();
    });

    it('create an instance', () => {
        expect(pipe).toBeTruthy();
    });

    it('should return false if end_date is not set', () => {
        const licensePlate: LicensePlateItem = {
            id: '1',
            lpn: 'ABC123',
            lps: 'XYZ',
            lpc: '12345',
            registered: '2023-01-01'
        };
        expect(pipe.transform(licensePlate)).toBe(false);
    });

    it('should return true if end_date is in the past', () => {
        const licensePlate: LicensePlateItem = {
            id: '1',
            lpn: 'ABC123',
            lps: 'XYZ',
            lpc: '12345',
            registered: '2023-01-01',
            end_date: '2023-01-01'
        };
        expect(pipe.transform(licensePlate)).toBe(true);
    });

    it('should return false if end_date is in the future', () => {
        const futureDate = new Date();
        futureDate.setFullYear(futureDate.getFullYear() + 1);
        const licensePlate: LicensePlateItem = {
            id: '1',
            lpn: 'ABC123',
            lps: 'XYZ',
            lpc: '12345',
            registered: '2023-01-01',
            end_date: futureDate.toISOString()
        };
        expect(pipe.transform(licensePlate)).toBe(false);
    });

    it('should throw an error if end_date format is invalid', () => {
        const licensePlate: LicensePlateItem = {
            id: '1',
            lpn: 'ABC123',
            lps: 'XYZ',
            lpc: '12345',
            registered: '2023-01-01',
            end_date: 'invalid-date'
        };
        expect(() => pipe.transform(licensePlate)).toThrow(new Error('Invalid LPN end_date format'));
    });
});

