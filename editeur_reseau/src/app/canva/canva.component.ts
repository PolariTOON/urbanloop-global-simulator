import { Component, ViewChild, ElementRef, OnInit, HostListener } from '@angular/core';
import { Subscription } from 'rxjs-compat/Subscription';
import { NetworkService } from '../services/network.service';
 
@Component({
  selector: 'app-canva',
  templateUrl: './canva.component.html',
  styleUrls: ['./canva.component.scss']
})
export class CanvaComponent implements OnInit {

    @HostListener('window:resize')
    onResize() {
        this.canvaHeight = Math.floor(window.innerHeight * 0.91);
        this.canvaWidth = Math.floor(window.innerWidth  * 0.75);
        this.canvas.nativeElement.height = this.canvaHeight;
        this.canvas.nativeElement.width = this.canvaWidth;
        if (!this.firstResize) {
            this.centerCircles();
            this.update();
        } else
            this.firstResize = false;
    }

	@ViewChild('canvas', { static: true })
    canvas: ElementRef<HTMLCanvasElement>;
	canvasElement; //El�ment canvas
	ctx: CanvasRenderingContext2D; //Contexte
	
	networkSubscription: Subscription;
	linkingSubscription: Subscription;
	editingSubscription: Subscription;
	editedSubscription: Subscription;
	newElementSubscription: Subscription;
	removingSubscription: Subscription;
	newNetworkSubscription: Subscription;
	convertSubscription: Subscription;
	removeLinkSubscription: Subscription;
	goToLinkSubscription: Subscription;
    goToLoopSubscription: Subscription;
    jsonSubcription: Subscription;
    optionsSubscription: Subscription
	
    //Variables relatives � l'affichage
    canvaWidth; //Largeur du canvas
    canvaHeight; //Hauteur du canvas
    fontSize: number = 10; //Taille de la police
    baseRadius = 10; //Rayon de base d'un cercle
    factor: number = 1; //Facteur de zoom
    zoomPower: number; //Puissance du zoom
    firstResize: boolean = true; //Le 1er resize est sp�cial car on n'update pas
    options: any; //Diff�rentes options d'affichage
    
    //Variables d�crivant le r�seau
	network: any; //R�seau
	circles: any[]; //Liste des cercles
    links: any[]; //Liste des liens
    loops: any[]; //Liste des boucles 
    
    //Variables d'id
	nextCircleId: number; //Prochain id de cercle
    nextLinkId: number; //Prochain id de lien
    nextLoopId: number; //Prochain id de boucle
    nextBridgeId: number; //Prochain id de pont
    
    //Variables relatives � un �v�nement
	down: boolean = false; //Vrai s'il y a clique
	previous: number[]; //Position pr�c�dente de la souris
	linking: boolean; //Vaut vrai si un lien est entrain d'�tre cr��
	editing: boolean; //Vaut vrai si on est entrain d'�dier
	removing: boolean; //Vaut vrai si on est entrain de supprimer
    selected: number; //Vaut l'index du cercle s�lectionn�, -1 sinon
    linkingFrom: number; //Origine du lien

    constructor(private networkService: NetworkService) { }

    ngOnInit() {		
		this.canvasElement = document.querySelector('canvas');
		//R�cup�ration du contexte
		this.ctx = this.canvas.nativeElement.getContext('2d');
		this.ctx.textAlign = 'center';
        this.onResize();
		
		this.newNetwork();
		//Ajout d'�v�nements de la souris
		const y = this;
		
		//D�tection du click
		document.body.onmousedown = function() {
			y.down = true;
		};
		document.body.onmouseup = function() {
			y.down = false;
		}
		
		//Gestion du zoom avec la molette
		document.getElementById("canvas").onwheel = function(event) {
			y.processZoom(-1 * Math.sign(event.deltaY));
            y.update();
		}
		
		//Observables
		// Synchronisation du r�seau
		this.networkSubscription = this.networkService.networkSubject.subscribe(
			(network: Object) => {
				this.network = network;
			}
		);
		this.networkService.emitNetworkSubject();
        
        // Synchronisation des options
        this.optionsSubscription = this.networkService.optionsSubject.subscribe(
            (options: any) => {
                this.options = options;
                this.zoomPower = options.zoom;
                this.update();
            }
        );
        this.networkService.emitOptionsSubject();
        
		// Mise � jour de l'�tat de liaison
		this.linkingSubscription = this.networkService.linkingSubject.subscribe(
			(linking: boolean) => {
				this.linking = linking;
				if (!linking) {
					this.linkingFrom = -1;
					this.update();
				}
			}
		);
		
        // Synchronisation de l'�tat d'�dition
		this.networkService.emitLinkingSubject();
		this.editingSubscription = this.networkService.editingSubject.subscribe(
			(editing: boolean) => {
				this.editing = editing;
			}
		);
		this.networkService.emitEditingSubject();
		
        // R�ception de l'�l�ment modifi�
		this.editedSubscription = this.networkService.editedSubject.subscribe(
			(elt: any) => {
				if (elt.hasOwnProperty('x')) {
                    //Cas o� elt est un cercle
					for (let i = 0; i < this.circles.length; i++) 
						if (this.circles[i].id == elt.id)
							this.circles[i] = elt;
				}
				else if (!elt.hasOwnProperty('isLoop')) {
                    //Cas o� elt est un lien
					for (let i = 0; i < this.links.length; i++) {
						const link = this.links[i];
						if (link.id == elt.id) {
							this.links[i] = elt;
							if (elt.old_length != elt.length) {
                                //Si la longueur a �t� modifi�e, il faut d�placer les cercles du liens
								let circle1 = this.getCircle(link.from);
								let circle2 = this.getCircle(link.to);
                                
                                let sourceX, sourceY, shift;
                                
                                if (elt.source == 'middle') {
                                    sourceX = (circle1.x + circle2.x) / 2;
                                    sourceY = (circle1.y + circle2.y) / 2;
                                    shift = (elt.length - elt.old_length) / 2;
                                } else {
                                    const ref = elt.source == 'from' ? circle1: circle2;
                                    sourceX = ref.x;
                                    sourceY = ref.y
                                    shift = elt.length - elt.old_length;
                                }
                                
                                if (elt.source == 'middle' || elt.source == 'to') {
                                    const i = this.circles.indexOf(circle1);
                                    this.circles[i] = this.moveCircle(circle1, sourceX, sourceY, shift, -1);
                                }
                                if (elt.source == 'middle' || elt.source == 'from') {
                                    const j = this.circles.indexOf(circle2);
                                    this.circles[j] = this.moveCircle(circle2, sourceX, sourceY, shift, -1);
                                }								
							}
						}
					}
				} else {
                    //Cas o� elt est une boucle
                    for (let i = 0; i < this.loops.length; i++)
                        if (this.loops[i].id == elt.id) {
                            delete elt.isLoop;
                            this.loops[i] = elt;
                        }
                }
				this.update();
			}
		);
		
        // R�ception de l'ordre de cr�ation d'un nouvel �l�ment
		this.newElementSubscription = this.networkService.newElementSubject.subscribe(
			(type: string) => {
				this.createCircle(this.canvasElement.width/2, this.canvasElement.height/2, type == 'station' ? 4: 50, null, type, 1)
				this.unToggleAll();
				this.update()
			}
		);
		
        // Synchronisation de l'�tat de suppression
		this.removingSubscription = this.networkService.removingSubject.subscribe(
			(removing: boolean) => {
				this.removing = removing;
			}
		);
		this.networkService.emitRemovingSubject();
		
        // R�ception de l'ordre de reset du r�seau
		this.newNetworkSubscription = this.networkService.newNetworkSubject.subscribe(
			() => {
				y.newNetwork()
			}
		);
		
        // R�ception de l'ordre d'exportation
		this.convertSubscription = this.networkService.convertSubject.subscribe(
			() => {
				y.convertNetwork();
				y.networkService.export();
			}
		);
		
        // R�ception de l'ordre de suppression d'un lien
		this.removeLinkSubscription = this.networkService.removeLinkSubject.subscribe(
			(id: number) => {
				this.removeLink(id);
				this.update();
			}
		);
		
        // R�ception de l'ordre d'�dition d'une sections
		this.goToLinkSubscription = this.networkService.goToLinkSubject.subscribe(
			(id: number) => {
                let link;
                this.links.forEach((linkElt) => {
                    if (linkElt.id == id)
                        link = linkElt;
                });
				if (!link.bridge) {
					link.from_name = this.getCircle(link.from).name;
					link.to_name = this.getCircle(link.to).name;
				} else {
                    link.from_name = 'Switch in';
                    link.to_name = 'Switch out';
                }
				link.old_length = link.length;
                link.old_angle = link.angle;
				this.networkService.emitEditedElementSubject({ elt: link, links: [], loop: {}});
			}
		);
        
        // R�ception de l'ordre d'�dition d'une boucle
		this.goToLoopSubscription = this.networkService.goToLoopSubject.subscribe(
			(id: number) => {
                let loop = this.getLoop(id);
                loop['isLoop'] = true;
				this.networkService.emitEditedElementSubject({ elt: loop, links: [], loop: {}});
			}
		);
        
        // Importation d'un r�seau
        this.jsonSubcription = this.networkService.jsonSubject.subscribe(
            (network) => {
                this.networkService.init();
                this.newNetwork();
                this.convertFromNetwork(network);
                this.update();
            }
        );
	}
    
//FONCTIONS GERANT LES CERCLES

    //Cr�e un cercle
    createCircle(x: number, y: number, max_pods: number, name: string, type: string, station_type: number) {
        
        let elt = {
            id: this.nextCircleId++,
            x: x,
            y: y,
            r: this.baseRadius * this.factor,
            loopId: -1
        };
        if (type == 'bridge') {
            //Quand on cr�e un pont, on cr�e aussi un deuxi�me cercle et on le lie
            elt['type'] = 'switch_in';
            this.circles.push(elt);
            
            let elt2 = Object.assign({}, elt);
            elt2['type'] = 'switch_out';
            elt2['id'] = this.nextCircleId++;
            elt2.x += elt.r * 4;

            this.circles.push(elt2);
            
            const n = this.circles.length - 1;
            this.linkBridge(n-1, n, 16.67, null, null);
        } else {
            //Cas d'un non-switch
            elt['name'] = name != null ? name: type + ' ' + (this.nextCircleId-1);
            elt['type'] = type;
            elt['max_pods'] = max_pods;
            if (type == 'station')
                elt['station_type'] = station_type;
            this.circles.push(elt);
        }
    }
    
    //Renvoie un cercle selon l'id
    getCircle(id: number) {
		for (const circle of this.circles)
			if (circle.id == id)
				return circle;
		return null;
    }
    
    // Renvoie le deuxieme cercle ayant un lien vers le cercle d'identifiant id
    getSecondCircleHavingLinkToCircleOfId(id: number)
    {
        let circletrouve = false;
        for (const link of this.links)
        {
            if (link.to == id)
            {
                if (circletrouve)
                {
                    return this.getCircle(link.from);
                }
                else
                {
                    circletrouve = true;
                }
            }
        }
        return null;
    }

    // Renvoie le deuxieme cercle ayant un lien qui vient du cercle d'identifiant id
    getSecondCircleHavingLinkFromCircleOfId(id: number)
    {
        let circletrouve = false;
        for (const link of this.links)
        {
            if (link.from == id)
            {
                if (circletrouve)
                {
                    return this.getCircle(link.to);
                }
                else
                {
                    circletrouve = true;
                }
            }
        }
        return null;
    }

    
    //D�place un cercle selon un point de rep�re
    moveCircle(circle, centerX: number, centerY: number, shift: number, max: number) {

		const angle = this.angle(circle.x, circle.y, centerX, centerY);
		const norm = this.distance(circle.x, circle.y, centerX, centerY);
        
		const scale = max > -1 ? norm / max: this.factor; 
		const side = circle.x < centerX? -1: 1;
		let coef = shift * side * scale;
        if (max > -1)
            coef *= this.zoomPower * this.circles.length;
        
		circle.x += Math.cos(angle) * coef;
        circle.y += Math.sin(angle) * coef;
        
		return circle;
	}
    
    //Supprime un cercle + les potentiels liens et boucles auquels il appartient
    removeCircle(id: number) {
		for (let i = 0; i < this.circles.length; i++)
			if (this.circles[i].id == id) {
				const circle = this.circles[i];
                this.removeLoop(circle.id);
				this.circles.splice(i, 1);
				for (let j = 0; j < this.links.length; j++) {
					const link = this.links[j];
					if (link.from == id || link.to == id) {
                        //Si le lien est un bridge il faut diminuer tous les bridgeId de 1
                        if (link.bridge) {
                            for (let k = 0; k < this.circles.length; k++) {
                                const circleBis = this.circles[k];
                                if (this.isSwitch(circleBis.id) && circleBis.link > circle.link)
                                    this.circles[k].link--;
                            }
                            this.nextBridgeId--;
                        }
                        
						this.links.splice(j--, 1);
					}
				}
				if (circle.type == 'switch_in' || circle.type == 'switch_out')
                    //Dans le cas d'un bridge on supprime aussi l'autre switch
					this.removeCircle(circle.linked);
				if (this.removing)
					this.networkService.toggleRemove();
				return;
			}
	}
    
    //G�re le click sur un cercle
    findCircle(x: number, y: number) {
		let found: boolean = false;
		for (let i = 0; i < this.circles.length; i++) {
		  const circle = this.circles[i];
			if (this.distance(circle.x, circle.y, x, y) < circle.r) {
                //Cas o� on a cliqu� sur un cercle
				if (this.linking) {
                    //Cas o� on veut cr�er un lien
					if (this.linkingFrom == -1)
                        //Si on a cliqu� sur le cercle source
						this.linkingFrom = circle.id;
					else 
                        //Si on a cliqu� sur le cercle cible
						this.createLink(this.linkingFrom, circle.id, 16.67, false, null, null, false);
				} else if (this.editing) {
                    //Cas o� on veut �diter un cercle
					const links = this.convertLinks(circle.id);
                    const loop = this.convertLoop(circle.loopId);
                    if (this.isSwitch(circle.id))
                        circle.bridge_name = this.getBridgeName(circle.id);
					this.networkService.editElement({ elt: circle, links: links, loop: loop });
				}
				else if (this.removing)
                    //Cas o� on veut supprimer un cerlce
					this.removeCircle(circle.id);
				else
                    //Cas o� on veut juste d�placer un cercle
					this.selected = i;
				found = true;
			}
		}
		if (!found)
			this.unToggleAll();
	}
    
//FONCTIONS ANNEXES SUR LES CERCLES

    //Renvoie la distance entre 2 cerlces, pond�r� par le zoom
    distanceCircles(id1: number, id2: number) {
        const circle1 = this.getCircle(id1);
        const circle2 = this.getCircle(id2);
        return this.distance(circle1.x, circle1.y, circle2.x, circle2.y) / this.factor; 
	}
    
    //Calcul l'angle entre 2 cerlces
    angleCircles(id1: number, id2: number) {
        const circle1 = this.getCircle(id1);
        const circle2 = this.getCircle(id2);
        return this.angle(circle1.x, circle1.y, circle2.x, circle2.y);
    }
    
	//D�tecte si un les cercles ne sont pas d�j� origine ou destination d'un lien
    alreadyLinked(id1, id2) {
		for (const link of this.links)
			if (!link.bridge && (link.from == id1 || link.to == id2))
				return true;
		return false;
	}
	
    //Renvoie vrai si l'id est un switch in ou switch out
	isSwitch(id: number) {
        const circle = this.getCircle(id);
		return circle.type == 'switch_in' || circle.type == 'switch_out';
	}
    
    //Centre le centre de gravit� des cercles
    centerCircles() {

        let centerX = 0;
        let centerY = 0;
        this.circles.forEach((circle) => {
            centerX += circle.x;
            centerY += circle.y;
        });
        centerX = centerX / this.circles.length - this.canvaWidth / 2;
        centerY = centerY / this.circles.length - this.canvaHeight / 2;

        /*
        J'ai commente ceci car ca changeait la place des stations/sheds avec le systeme de bridge-deviation
        for (let circle of this.circles) 
        {
            circle.x -= centerX;
            circle.y -= centerY;
        }
        */
    }
    
    getCircleIndex(id: number) {
        for (let i = 0; i < this.circles.length; i++)
            if (this.circles[i].id == id)
                return i;
        return -1;
    }
    
    goingFrom(id: number) {
        for (const link of this.links)
        {
            if (!link.bridge && link.from == id)
            {
                return link;
            }
        }
        return null;
    }

    // La version adaptee au changement sur les mini-boucle, avec les bridge-deviation pour chaque station
    // Renvoie le lien qui est un bridge s'il y en a
    goingFromConsideringBridgesForCircle(id: number)
    {
        let linkFound = null;
        let bridgeLinkFound = null;
        let hasFoundBridgeLink = false;

        for (const link of this.links)
        {
            if (!link.bridge && link.from == id)
            {
                linkFound = link;
            }
            else if (link.bridge && link.from == id)
            {
                bridgeLinkFound = link;
                hasFoundBridgeLink = true;
            }
        }

        if (hasFoundBridgeLink)
        {
            return bridgeLinkFound;
        }
        else
        {
            return linkFound;
        }
    }

    //FONCTIONS GERANT LES LIENS

    //Cr�e un nouveau lien
    // TODO : ne pas pouvoir linker des switch de boucles diff�rentes
    createLink(id1: number, id2: number, speed: number, bridge: boolean, bridgeName: string, loopName: string, isSpecial: boolean) {
        const b = !bridge && this.isSwitch(id1) && this.isSwitch(id2) && this.getCircle(id1).linked == id2;
        const name = bridgeName != null ? bridgeName: 'bridge ' + this.nextBridgeId;
        
        if (!b && id1 != id2 && (bridge || !this.alreadyLinked(id1, id2))) {
			this.links.push({
				id: this.nextLinkId++,
				from: id1,
				to: id2,
				inLoop: false,
				speed: speed,
				length: this.distanceCircles(id1, id2),
                angle: this.angleCircles(id1, id2),
				bridge: bridge,
                name: bridge ? name: null,
                source: 'middle'
            });
		}
        if (this.linking)
        {
            this.networkService.unlink();
        }

        // Si on est pas dans un cas de section sur un bridge vers une station (nouveau format de bridge)
        if (!isSpecial)
		    this.checkForLoops(loopName);
    }
    
    /*
    Modifie un lien qui va representer un pnt
    (fait sujite a la suppression des mini-boucles et l'introduction des bridges dans les sections)
    */
    modifyLinkForBridge(id1: number, id2: number, bridgeName: string) 
    {
        for (let i = 0; i < this.links.length; i++) 
        {
            const link = this.links[i];
            if ((link.to == id1 && link.from == id2) || (link.to == id2 && link.from == id1))
            {
                link.bridge = true;
                link.name = bridgeName;
            }
        }
	}
    
    //Renvoie un lien selon l'id
    getLink(id: number) {
		for (const link of this.links)
			if (!link.bridge && link.id == id)
				return link;
		return null;
    }
    
    // Renvoi le premier lien partant d'un cercle d'id id
    getLinkFromCircleOfId(id: number)
    {
        for (const link of this.links)
            if (link.from == id)
                return link;
        return null;
    }

    // Renvoi le premier lien allant vers un cercle d'id id
    getLinkToCircleOfId(id: number)
    {
        for (const link of this.links)
            if (link.to == id)
                return link;
        return null;
    }
    
    //Renvoie l'indice d'un lien selon l'id
    findLink(id: number) {
		for (let i = 0; i < this.links.length; i++)
			if (this.links[i].from == id && !this.links[i].bridge)
				return i;
		return -1;
	}
    
    //Supprimer un lien selon l'id + la boucle si besoin
	// TODO: int�grer � removeCircle
    removeLink(id: number) {
		for (let i = 0; i < this.links.length; i++) {
            const link = this.links[i];
			if (link.id == id) {
                if (link.inLoop) {
                    const loopId = this.getCircle(link.from).loopId;
                    this.removeLoop(loopId);
                }
				this.links.splice(i, 1);
				return;
			}
        }
	}
    
//FONCTIONS ANNEXES SUR LES LIENS

    //Cr�e un lien entre deux switch
    linkBridge(i: number, j: number, speed: number, bridgeName: string, loopName: string) {
        const id1 = this.circles[i].id;
        const id2 = this.circles[j].id;

        this.circles[i].link = this.nextBridgeId;
        this.circles[i].linked = id2;
        this.circles[i].name = this.getCircle(id1).type + id1;
        this.circles[j].link = this.nextBridgeId++;
        this.circles[j].linked = id1;
        this.circles[j].name = this.getCircle(id2).type + id2;

        this.createLink(id1, id2, speed, true, bridgeName, loopName, false);
    }

    /*
    Lie 2 switchs qui ont ete deja lies en tant que sections 
    (a cause de la suppression des mini-boucles et l'introduction des bridges dans les sections)
    */
    linkBridgeWhenAlreadyLinked(i: number, j: number, speed: number, bridgeName: string, loopName: string) {
        const id1 = this.circles[i].id;
        const id2 = this.circles[j].id;

        this.circles[i].link = this.nextBridgeId;
        this.circles[i].linked = id2;
        this.circles[i].name = this.getCircle(id1).type + id1;
        this.circles[j].link = this.nextBridgeId++;
        this.circles[j].linked = id1;
        this.circles[j].name = this.getCircle(id2).type + id2;

        this.modifyLinkForBridge(id1, id2, bridgeName);
    }
    
    // Convertit les liens pour les envoyer � l'�dition
    convertLinks(id: number) {
		let res = [];
		this.links.forEach((link) => {
			if (link.bridge && (link.from == id || link.to == id)) {
                //Cas d'un pont
				res.push({
					id: link.id,
					type: 'bridge',
                    name: link.name
				});
			} else if (link.from == id) {
                //Cas d'une section arrivante
				const to = this.getCircle(link.to).name;
				res.push({
					id: link.id,
					type: 'from',
					to: to
				});
			}
			else if (link.to == id) {
                //Cas d'une section partante
				const from = this.getCircle(link.from).name;
				res.push({
					id: link.id,
					type: 'to',
					from: from
				});
			}
		});
		return res;
	}
    
    getBridgeName(id: number) {
        const circle = this.getCircle(id);
        let res;
        this.links.forEach((link) => {
            if (link.bridge && ((circle.type == 'switch_in' && link.from == id) ||
                                (circle.type == 'switch_out' && link.to == id)))
                res = link.name;
        });
        return res;
    }
    
//FONCTIONS GERANT LES BOUCLES

    //V�rifie s'il faut cr�er une boucle
    checkForLoops(name: string) {
		for (let i = 0; i < this.links.length; i++) {
			const link = this.links[i];
			if (!link.inLoop && !link.bridge) {
				let stop = false; //Vaut vrai quand le parcours est termin�
				let isLoop = false; //Vaut vrai si une boucle doit �tre cr��e
				let links = Object.assign([], this.links); //Liste des liens � parcourir
				let next = link.to; //Prochain lien � parcourir
				let way = [i]; //On construit la liste des liens de la boucle
				const id = link.from;
				
                //On d�vient tous les liens comme non marqu�s
				for (let link of links)
					link.checked = false;
				links[i].checked = true;
				
				while (!stop && !isLoop) {
					//On cherche le prochain lien
					const nextLink = this.findLink(next);
					if (nextLink == -1)
						//S'il n'existe pas la boucle n'est pas ferm�e
						stop = true;
					else if (links[nextLink].checked)
						//Si le lien est d�j� marqu�, on est revenu au point de d�part
						isLoop = true;
					else {
						//Sinon, on ajoute le lien au chemin et on passe au suivant
						way.push(nextLink);
						next = links[nextLink].to;
					}
				}
				if (isLoop) {
					let loop = []
					for (const j of way) {
                        const circleId = this.links[j].from;
                        for (let circle of this.circles)
                            if (circle.id == circleId)
                                circle.loopId = this.nextLoopId;
						this.links[j].inLoop = true;
						loop.push(circleId);
					}
					this.loops.push({
						id: this.nextLoopId++,
						name: name != null ? name: 'untitled loop ' + this.nextLoopId,
						loop: loop
					});
				}
			}
		}
	}
    
    getLoop(id: number) {
        for (const loop of this.loops)
            if (loop.id == id)
                return loop;
        return null;
    }
    
    //Supprime une boucle selon l'id
    removeLoop(id: number) {
		for (let k = 0; k < this.loops.length; k++) {
			const loop = this.loops[k].loop;
			if (loop.includes(id)) {
                loop.forEach((circleId) => {
                    const index = this.getCircleIndex(circleId);
                    if (index != -1) {
                        //On enl�ve le loopId
                        this.circles[index].loopId = -1;
                        //En enl�ve les liens de la boucle
                        for (let link of this.links) 
                            if (link.from == circleId || link.to == circleId)
                                link.inLoop = false;
                    }
                });
				this.loops.splice(k--, 1);
				return;
			}
		}
	}
    
    convertLoop(id: number) {
        for (const loop of this.loops)
            if (loop.id == id)
                return {
                    id: id,
                    name: loop.name
                };
        return null;
    }
    
//FONCTIONS RELATIVES � L'AFFICHAGE    
    
    //Mets � jour l'affichage
    update() {
		this.ctx.clearRect(0, 0, this.canvasElement.width, this.canvasElement.height);
		
		//Affichage des cerlces
		this.circles.forEach((circle) => {
			//Couleur
			if (circle.id == this.linkingFrom)
				this.ctx.fillStyle = 'yellow';
			else
				switch(circle.type) {
					case 'station': {
						this.ctx.fillStyle = 'red';
						break;
					}
					case 'shed': {
						this.ctx.fillStyle = 'blue';
						break;
					}
					case 'switch_in':
					case 'switch_out': {
						this.ctx.fillStyle = 'green';
						break;
					}
				}
				
			//Tra�age du cercle
			this.ctx.beginPath();
			this.ctx.arc(circle.x, circle.y, circle.r, 0, Math.PI * 2);
			this.ctx.stroke();
			this.ctx.fill();
			//Affichage du texte
            this.ctx.fillStyle = 'black';
            this.ctx.textAlign = 'center';
            if (!this.isSwitch(circle.id) && ((circle.type == 'station' && this.options.station)) || (circle.type == 'shed' && this.options.shed))
                this.ctx.fillText(circle.name, circle.x, circle.y + circle.r + 10);
            else if (circle.type == 'switch_in' && this.options.switch)
                this.ctx.fillText(circle.name, circle.x, circle.y + circle.r + 10);
            else if (circle.type == 'switch_out' && this.options.switch)
                this.ctx.fillText(circle.name, circle.x, circle.y + circle.r + 10);
            this.ctx.closePath();
		});
		
		//Affichage des liens
		this.links.forEach((link) => {
			let circle1 = this.getCircle(link.from);
			let circle2 = this.getCircle(link.to);
			this.ctx.beginPath();
			//Affichage de la ligne
			this.ctx.moveTo(circle1.x, circle1.y);
			this.ctx.lineTo(circle2.x, circle2.y);
            this.ctx.stroke();
            
            if (!link.bridge) {
                //Calculs
                const angle = this.angle(circle1.x, circle1.y, circle2.x, circle2.y) + 5 * Math.PI / 6;
                let side = 1;
                if (circle2.x < circle1.x)
                    side = -1
                const coef = 11 * side * this.factor;
                //Affichage des fl�ches
                this.ctx.lineTo(circle2.x + Math.cos(angle) * coef, circle2.y + Math.sin(angle) * coef);
                this.ctx.stroke()
                this.ctx.moveTo(circle2.x, circle2.y);
                this.ctx.lineTo(circle2.x + Math.cos(angle + Math.PI/3) * coef, circle2.y + Math.sin(angle + Math.PI/3) * coef);
                this.ctx.stroke();
            } else if (this.options.bridge) {
                //Affichage du nom du bridge
                const centerX = (circle1.x + circle2.x) / 2;
                const centerY = (circle1.y + circle2.y) / 2;
                this.ctx.fillStyle = 'black';
                this.ctx.textAlign = 'center';
                this.ctx.fillText(link.name, centerX, centerY);
                this.ctx.closePath();
            }
            
			this.ctx.closePath();
		});
		
		//Affiche des boucles
        if (this.options != null && this.options.loop) {
            this.loops.forEach((loop) => {
                const n = loop.loop.length;
                let centerX = 0;
                let centerY = 0;
                loop.loop.forEach((circleId) => {
                    const circle = this.getCircle(circleId);
                    centerX += circle.x;
                    centerY += circle.y;
                });
                centerX /= n;
                centerY /= n;
                this.ctx.beginPath();
                this.ctx.fillStyle = 'black';
                this.ctx.fillText(loop.name, centerX, centerY);
            });
        }
	}
    
    goToZoom(factor: number) {
        let shift;
        while (!this.equalsAround(this.factor, factor)) {
            shift = this.factor < factor ? 0.01: -0.01;
            this.processZoom(shift);
        }
        this.update();
    }
    
    //G�re le zoom
    processZoom(shift: number) {   
        if (this.circles.length == 1) {
            const circle = this.circles[0];
            if (shift > 0 || circle.r > 2) {
                const oldR = circle.r;
                this.circles[0].r += this.zoomPower * shift;
                if (this.circles[0].r < 2)
                    this.circles[0].r = 2;
                this.factor *= this.circles[0].r / oldR;
            }
        } else {
            //On commence par calculer le centre de gravit� des cercles
            let centerX = 0;
            let centerY = 0;
            this.circles.forEach((circle) => {
                centerX += circle.x;
                centerY += circle.y;
            });
            centerX /= this.circles.length;
            centerY /= this.circles.length;
            
            //On calcule ensuite la distance maximale entre un cercle et le centre de gravit�
            let norms = [];
            this.circles.forEach((circle) => {
                norms.push(this.distance(centerX, centerY, circle.x, circle.y));
            });
            const max = Math.max.apply(null, norms);
                
            //Enfin on d�place tous les cercles d'un certain ratio par rapport au centre de gravit�
            //D'apr�s le th�or�me de Thal�s le ratio est le m�me pour tous
            //M�me pour les distances entre les cercles proches
            let first: boolean = true;
            let fact: number;
            let norm, norm2;
            for (let i = 0; i < this.circles.length; i++) {
                const circle = this.circles[i];
                if (shift > 0 || circle.r > 2) {
                    if (first)
                        norm = this.distance(circle.x, circle.y, centerX, centerY);
                    this.circles[i] = this.moveCircle(circle, centerX, centerY, shift, max);
                    if (first) {
                        //On r�cup�re le facteur de cette �tape de zoom
                        norm2 = this.distance(circle.x, circle.y, centerX, centerY);
                        fact = norm2 / norm;
                        //On ajoute au facteur de zoom total
                        this.factor *= fact;
                        first = false;
                    }
                    //On change aussi le rayon des cercles
                    circle.r *= fact;
                }
            }
        }
    }
	
    //Change la police d'�criture
    scaleFont() {
		this.ctx.font = this.fontSize.toString() + 'px serif';
	}
    
    //Modifie la viewbox du r�seau
    updateViewBox() {
        this.network.view_box = {
            x: 0,
            y: 0,
            width: this.canvaWidth,
            height: this.canvaHeight
        };
        this.networkService.updateNetwork(this.network);
    }
    
//FONCTIONS D'EVENEMENTS    
    
    //Tente de s�lectionner un cercle l� o� il y a eu un click
    select(event: any) {
		const shift = this.getShift();
		this.findCircle(event.x - shift.x, event.y - shift.y);
		this.update();
	}
	
    //D�place tous les cercles ou seulement celui s�lectionn�
	move(event: any) {
		if (this.down && !this.linking && !this.editing) {
			const shift = this.getShift();
			if (this.previous != null) {
				const shiftX = event.x - this.previous[0];
				const shiftY = event.y - this.previous[1];
				if (this.selected != -1) {
					this.circles[this.selected].x += shiftX;
					this.circles[this.selected].y += shiftY;
					const circle = this.circles[this.selected];
					for (let link of this.links) {
						if (link.from == circle.id || link.to == circle.id) {
							let id = link.to == circle.id ? link.from: link.to;
                            
                            const dist = this.distanceCircles(id, circle.id)
							link.length = dist;
                            link.old_length = dist;
                            
                            const angle = this.angleCircles(id, circle.id)
                            link.angle = angle;
                            link.old_angle = angle;
						}
					}
				} else {
					for (let circle of this.circles) {
						circle.x += shiftX;
						circle.y += shiftY;
					}
				}
			}
			this.previous = [event.x, event.y];
			this.update();
		}
	}
	
    //D�s�lectionne tout
	drop() {
		this.selected = -1;
		this.previous = null;
	}
    
//FONCTIONS UTILITAIRES

    //Renvoie l'angle entre le vecteur d�fini par deux points et l'axe des abscisses
    angle(x1: number, y1: number, x2: number, y2: number) {
		const vectX = x2 - x1;
		const vectY = y2 - y1;
		return Math.atan(vectY / vectX);
	}
	
    //Renvoie la distance entre deux points
	distance(x1: number, y1: number, x2: number, y2: number) {
		return Math.sqrt((x2-x1)**2 + (y2-y1)**2);
	}
    
    //D�s�lectionne toutes les options
    unToggleAll() {
		this.selected = -1;
		if (this.linking)
			this.networkService.unlink();
		if (this.editing)
			this.networkService.toggleEdit();
		if (this.removing)
			this.networkService.toggleRemove();
	}
	
    //Calcule le d�calage du canvas par rapport � la page
	getShift() {
		const rect = this.canvasElement.getBoundingClientRect();
		return { 
			x: rect.left,
			y: rect.top
		};
	}
    
    //R�initialise le mod�le �dtieur
	newNetwork() {
		this.selected = -1;
		this.circles = [];
		this.nextCircleId = 0;
		this.links = [];
		this.nextLinkId = 0;
		this.loops = [];
		this.nextLoopId = 0;
		this.factor = 1;
		this.nextBridgeId = 0;
		this.update();
	}
    
    //Convertit seconde en heure minute
    convertSecondsToTime(seconds: number) {
        seconds /= 60;
        return {
            hours: Math.floor(seconds / 60),
            minutes: seconds % 60
        }
    }
    
    //Convertit heure minute en secondes
    convertTimeToSeconds(hours: number, minutes: number) {
        return hours * 3600 + minutes * 60;
    }
    
    //Renvoie vrai si la boucle contient un switch dont l'autre switch n'est pas dans une boucle
    containsSwitchLinkedWithAloneSwitch(loop) {
        for (const circleId of loop.loop) {
            const circle = this.circles[circleId];
            const other = this.getCircle(circle.linked);
            if (this.isSwitch(circle.id) && other.loopId == -1)
                return true;
        }
        return false;
    }
    
    //Egalit� de float
    equalsAround(a: number, b: number) {
        return a > b - 0.01 && a < b + 0.01;
    }


//FONCTIONS DE CONVERTION

    //Convertit le r�seau mod�le �dtieur -> simulateur
	convertNetwork() {
        this.goToZoom(1);
        
        this.updateViewBox();
		this.network.loops = [];
		this.network.bridges = [];
        this.network.time = this.convertTimeToSeconds(this.network.hours, this.network.minutes);

        let numberStationsWronglyPlaced = 0;
        let numberShedsWronglyPlaced = 0;
        
        console.log("\n\nCONVERT NETWORK\n\n");

        //On parcourt les boucles
		for (let i = 0; i < this.loops.length; i++) {
			const loop = this.loops[i];
            if (!this.containsSwitchLinkedWithAloneSwitch(loop)) {
                this.network.loops.push({
                    name: loop.name,
                    elements: [],
                    sections: [],
                    pods: []
                });
                //On parcourt les cercles de cette boucle
                loop.loop.forEach((circleId) => {
                    //On ajoute chaque cerlce
                    const circle = this.getCircle(circleId);
                    let elt = {
                        type: circle.type,
                        x: circle.x,
                        y: circle.y
                    }
                    if (this.isSwitch(circle.id)) {
                        elt['id_bridge'] = circle.link;
                        elt['pods'] = [];
                    } 
                    else 
                    {
                        elt['name'] = circle.name;
                        elt['pods'] = {
                            max: circle.max_pods,
                            count: circle.type == 'station' ? 0: circle.max_pods
                        };
                        if (elt.type == 'station') 
                        {
                            numberStationsWronglyPlaced ++;
                            elt['station_type'] = circle.station_type;
                            elt['travelers'] = {
                                count: 0, 
                                average_waiting_time: 0, 
                                all_time_count: 0
                            };
                        }
                        else if (elt.type == 'shed')
                        {
                            numberShedsWronglyPlaced ++;
                        }
                    }
                    this.network.loops[i].elements.push(elt);
                    //On ajoute ensuite une section

                    // Pas cela finalement ?
                    //const link = this.goingFromConsideringBridgesForCircle(circleId);

                    const link = this.goingFrom(circleId);

                    //console.log("link.speed = " + link.speed);
                    this.network.loops[i].sections.push(
                    {
                        speed: link.speed,
                        path: {
                            type: 'line'
                        }
                    });
                });
            }
        }

        // L'ordre est important ! On va d'abord stocker les bridges classiques puis les speciaux
        let classicalBridges = [];
        let specialBridges = [];

        //On parcourt tous les liens qui sont des bridge
        this.links.forEach((link) => 
        {
            const goingFromFrom = this.goingFrom(link.from);
            const goingFromTo = this.goingFrom(link.to);

            // Si le lien est un pont (sinon on l'a deja traite dans loops normalement)
            if (link.bridge && goingFromFrom != null && goingFromTo != null)
            {
                // CE QUI SUIT DECOULE DES MODIF FAITES SUR LES MINI-BOUCLES (maintenant un bridge relie la station au reseau)
                const circle1 = this.getSecondCircleHavingLinkFromCircleOfId(this.getCircle(link.from).id);
                const circle2 = this.getSecondCircleHavingLinkToCircleOfId(this.getCircle(link.to).id);
                
                if (circle1 == circle2 && circle1 != null)  // c'est le cas si c'est un pont-station
                {
                    // Les sections
                    let sectionsFound = [];

                    const linkFromCircle1 = this.getLinkFromCircleOfId(circle1.id);
                    sectionsFound.push(
                        {
                        speed: linkFromCircle1.speed,
                        path: {
                            type: 'line'
                        }
                    })

                    const linkToCircle1 = this.getLinkToCircleOfId(circle1.id);
                    sectionsFound.push(
                        {
                        speed: linkToCircle1.speed,
                        path: {
                            type: 'line'
                        }
                    })


                    // Les elements
                    let elements = [];

                    const elt1 =
                    {
                        type: circle1.type,
                        name: circle1.name,
                        x: circle1.x,
                        y: circle1.y,
                        pods: 
                        {
                            max: circle1.max_pods,
                            count: circle1.type == 'station' ? 0: circle1.max_pods
                        },
                        station_type: circle1.station_type
                    };
                    if (elt1.type == 'station') {
                        elt1['station_type'] = circle1.station_type;
                        elt1['travelers'] = {
                            count: 0, 
                            average_waiting_time: 0, 
                            all_time_count: 0
                        };
                    }

                    // Qu'un seul element dans ce cas
                    elements.push(elt1);


                    // On push le tout
                    specialBridges.push(
                    {
                        name: link.name,
                        sections: sectionsFound,
                        elements: elements,
                        pods: []
                    });
                }
                else    //Points classiques (ne reliant pas station/shed)
                {
                    let sectionsFound = [];

                    // Qu'une seule section dans ce cas-la
                    sectionsFound.push(
                    {
                        speed: link.speed,
                        path: {
                            type: 'line'
                        }
                    })

                    classicalBridges.push(
                    {
                        name: link.name,
                        pods: [],
                        sections: sectionsFound,
                        elements: []
                    });
                }
            }
        });

        // On rassemble les bridges classique et les speciaux 
        classicalBridges.forEach((classicalBridge) =>
        {
            this.network.bridges.push(classicalBridge);
        });
        specialBridges.forEach((specialBridge) =>
        {
            this.network.bridges.push(specialBridge);
        });
        ///////
        
        this.networkService.updateNetwork(this.network);

        if (numberStationsWronglyPlaced > 0 || numberShedsWronglyPlaced > 0)
        {
            console.log("%cIncorrect format " + numberShedsWronglyPlaced + " sheds et " + numberStationsWronglyPlaced + " stations", "color: red");
            console.log("%cThe json will not be accepted in the simulator", "color: red");
            console.log("Please integrate a bridge linking the sheds/stations individually to the place they are now");
        }
	}

    //Convertit le r�seau mod�le simulateur -> �diteur
    convertFromNetwork(network) {
        this.networkService.init();
        this.network = Object.assign({}, network);
        this.network.loops = [];
        this.network.bridges = [];
        this.networkService.updateNetwork(this.network);
        
        const time = this.convertSecondsToTime(network.time);
        this.network['hours'] = time['hours'];
        this.network['minutes'] = time['minutes'];
        
        let bridges = [];
        for (const bridge of network.bridges)
            bridges.push([]);

        network.loops.forEach((loop) => {        
            const firstId = this.nextCircleId;
            loop.elements.forEach((elt) => {
                if (elt.type != 'sensor') {
                    const statOrShed = elt.type == 'station' || elt.type == 'shed'
                    const max_pods = statOrShed ? elt.pods.max: null;
                    const name = statOrShed ? elt.name: null;
                    const station_type = statOrShed ? elt.station_type: null;
                    this.createCircle(elt.x, elt.y, max_pods, name, elt.type, station_type);
                    if (!statOrShed)
                    {
                        bridges[elt.id_bridge].push(this.circles.length - 1);
                    }
                }
            });
            const lastId = this.nextCircleId - 1;
            
            let i = firstId;
            loop.sections.forEach((section) => {
                if (i < lastId)
                    this.createLink(i++, i, section.speed, false, null, loop.name, false);
                else
                    this.createLink(lastId, firstId, section.speed, false, null, loop.name, false);
            });
        });
        this.centerCircles();
        

        for (let k = 0; k < bridges.length; k++) {
            const i = bridges[k][0];
            const j = bridges[k][1];
            const bridge = network.bridges[k];

            if (bridge.section != null)             // sur un bridge classique avec format section
            {
                this.linkBridge(i, j, bridge.section.speed, bridge.name, null);
            }
            else if (bridge.sections.length == 1)   // sur un bridge classique avec format sections
            {
                this.linkBridge(i, j, bridge.sections[0].speed, bridge.name, null);
            }
            else        // Sur un bridge de station/shed
            {
                this.linkBridgeWhenAlreadyLinked(i, j, bridge.sections[0].speed, bridge.name, null);

                ///////////////////////////////////////////
                ///// J'ai recopie  ceci, on le faisait pour les loops dans la meme fonction
                const firstId = this.nextCircleId;
                bridge.elements.forEach((elt) => {
                    if (elt.type != 'sensor') {
                        const statOrShed = elt.type == 'station' || elt.type == 'shed'
                        const max_pods = statOrShed ? elt.pods.max: null;
                        const name = statOrShed ? elt.name: null;
                        const station_type = statOrShed ? elt.station_type: null;
                        this.createCircle(elt.x, elt.y, max_pods, name, elt.type, station_type);
                        if (!statOrShed)
                            bridges[elt.id_bridge].push(this.circles.length - 1);
                    }
                });
                const lastId = this.nextCircleId - 1;

                this.createLink(lastId, j, bridge.sections[0].speed, false, bridge.name + "_from_station", null, true);
                this.createLink(i, lastId, bridge.sections[1].speed, false, bridge.name + "_to_station", null, true);
            }
        }
    }

}
