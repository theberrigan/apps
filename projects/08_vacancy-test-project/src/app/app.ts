import { Component, signal, computed, inject, OnInit, Signal, WritableSignal } from '@angular/core';
import { ReactiveFormsModule, FormsModule, FormControl, Validators } from '@angular/forms';
import { debounceTime } from 'rxjs/operators';

import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatListModule } from '@angular/material/list';
import { MatCardModule } from '@angular/material/card';
import { ProgressSpinnerMode, MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { IUser } from './models/user.interface';
import { UserService } from './services/user';



interface IUserStatus {
    name  : string;
    value : string;
}


@Component({
    selector: 'app-root',
    imports: [
        FormsModule,
        ReactiveFormsModule,
        MatFormFieldModule,
        MatInputModule,
        MatSelectModule,
        MatListModule,
        MatCardModule,
        MatProgressSpinnerModule,
    ],
    templateUrl: './app.html',
    styleUrl: './app.less'
})
export class App implements OnInit {
    protected readonly title = signal('naumen-test');

    private readonly userService = inject(UserService);

    protected users : WritableSignal<IUser[]> = signal([]);

    protected filteredUsers : Signal<IUser[]> = computed(() => {
        const searchTerm = this.searchTerm();

        return this.users().filter((user) => {
            return (
                (
                    this.status() === 'all' ||
                    this.status() === 'active' && user.active ||
                    this.status() === 'inactive' && !user.active
                ) &&
                (!searchTerm || user.name.toLowerCase().includes(searchTerm))
            );
        });
    });

    protected activeUser : WritableSignal<IUser | null> = signal(null);

    protected readonly userStatuses : IUserStatus[] = [
        {
            name: 'Все',
            value: 'all'
        },
        {
            name: 'Активные',
            value: 'active'
        },
        {
            name: 'Неактивные',
            value: 'inactive'
        },
    ];

    protected status : WritableSignal<string> = signal(this.userStatuses[0].value);

    protected searchTerm : WritableSignal<string> = signal('');

    protected searchControl = new FormControl(this.searchTerm());

    protected isLoading : WritableSignal<boolean> = signal(true);

    async ngOnInit () : Promise<void> {
        const users = await this.userService.fetchUsers();

        this.users.set(users);

        this.searchControl.valueChanges
            .pipe(debounceTime(500))
            .subscribe((searchTerm) => {
                searchTerm = (searchTerm || '').trim().toLowerCase();

                this.searchTerm.set(searchTerm);
                this.resetActiveUser();
            });

        this.isLoading.set(false);
    };

    onUserSelect (user : IUser) {
        this.activeUser.set(user);
    }

    onStatusChange () {
        this.resetActiveUser();
    }

    resetActiveUser () {
        this.activeUser.set(null);
    }

    resetSearchTerm () {
        this.searchTerm.set('');
    }
}
