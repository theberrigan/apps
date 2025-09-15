import {Component, OnInit, ViewEncapsulation} from '@angular/core';

@Component({
  selector: 'app-logo-neoride',
  templateUrl: './logo-neoride.component.svg',
  styleUrls: ['./logo-neoride.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class LogoNeorideComponent implements OnInit {

  constructor() {
  }

  neoColor: string = '#003A70';
  rideColor: string = '#008299';
  boobiesColor: string = '#003A70';

  ngOnInit(): void {
  }
}


