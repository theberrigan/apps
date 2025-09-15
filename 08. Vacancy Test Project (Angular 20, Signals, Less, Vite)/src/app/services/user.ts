import { Injectable } from '@angular/core';

import { IUser } from '../models/user.interface';



const USERS : IUser[] = [
    {
        id: 1,
        name: 'Александр Сергеев',
        email: 'alexandr.sergeev@mail.ru',
        active: true
    },
    {
        id: 2,
        name: 'Анна Иванова',
        email: 'anna.ivanova@gmail.com',
        active: false
    },
    {
        id: 3,
        name: 'Михаил Кузнецов',
        email: 'mikhail.kuznetsov@yahoo.com',
        active: true
    },
    {
        id: 4,
        name: 'Екатерина Смирнова',
        email: 'ekaterina.smirnova@yandex.ru',
        active: true
    },
    {
        id: 5,
        name: 'Павел Попов',
        email: 'pavel.popov@mail.ru',
        active: false
    },
    {
        id: 6,
        name: 'Светлана Соколова',
        email: 'svetlana.sokolova@gmail.com',
        active: true
    },
    {
        id: 7,
        name: 'Денис Федоров',
        email: 'denis.fedorov@hotmail.com',
        active: false
    },
    {
        id: 8,
        name: 'Дарья Николаева',
        email: 'darya.nikolaeva@rambler.ru',
        active: true
    },
    {
        id: 9,
        name: 'Артём Антонов',
        email: 'arteom.antonov@mail.ru',
        active: false
    },
    {
        id: 10,
        name: 'Виктория Сидорова',
        email: 'viktoria.sidorova@yandex.ru',
        active: true
    }
];


@Injectable({
    providedIn: 'root'
})
export class UserService {
    public async fetchUsers () : Promise<IUser[]> {
        return new Promise((resolve) => {
            setTimeout(() => resolve(USERS), 3000);
        });
    }
}
