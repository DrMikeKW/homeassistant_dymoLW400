class LabelPrinterCard extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    static get styles() {
        return `
            :host {
                --card-primary: #007AFF;
                --card-border-radius: 16px;
                --input-height: 44px;
                --transition-speed: 0.2s;
            }

            .card-content {
                padding: 24px;
                box-sizing: border-box;
            }
            
            .card-content * {
				box-sizing: border-box;
			}

            ha-card {
                border-radius: var(--card-border-radius);
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                box-shadow: 
                    0 4px 6px -1px rgba(0, 0, 0, 0.1),
                    0 2px 4px -1px rgba(0, 0, 0, 0.06);
                transition: transform var(--transition-speed), box-shadow var(--transition-speed);
            }

            ha-card:hover {
                box-shadow: 
                    0 10px 15px -3px rgba(0, 0, 0, 0.1),
                    0 4px 6px -2px rgba(0, 0, 0, 0.05);
            }

            .header {
                padding: 24px 24px 0;
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .header-icon {
                width: 32px;
                height: 32px;
                fill: var(--card-primary);
            }

            .header-title {
                font-size: 24px;
                font-weight: 600;
                color: #1D1D1F;
                margin: 0;
            }

            .form-group {
                margin-bottom: 24px;
            }
            
            .form-group:last-of-type {
                margin-bottom: 32px;
            }

            label {
                display: block;
                margin-bottom: 8px;
                font-size: 14px;
                font-weight: 500;
                color: #86868B;
            }

            input, select {
                width: 100%;
                height: var(--input-height);
                padding: 0 16px;
                border: 1.5px solid #E5E5EA;
                border-radius: 12px;
                font-size: 16px;
                color: #1D1D1F;
                background: #F5F5F7;
                transition: all var(--transition-speed);
                -webkit-appearance: none;
                appearance: none;
                backdrop-filter: blur(10px);
            }

            select {
                background-image: url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='%2386868B' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
                background-repeat: no-repeat;
                background-position: right 16px center;
                padding-right: 40px;
            }

            input:focus, select:focus {
                outline: none;
                border-color: var(--card-primary);
                box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1);
            }

            button {
                width: 100%;
                height: var(--input-height);
                background: var(--card-primary);
                border: none;
                border-radius: 12px;
                color: white;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all var(--transition-speed);
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }

            button:hover {
                background: #0066D6;
                transform: translateY(-1px);
            }

            button:active {
                background: #005BBF;
                transform: translateY(0);
            }

            .button-icon {
                width: 20px;
                height: 20px;
                fill: currentColor;
            }

            @media (prefers-color-scheme: dark) {
                ha-card {
                    background: rgba(28, 28, 30, 0.95);
                }

                .header-title {
                    color: #FFFFFF;
                }

                label {
                    color: rgba(255, 255, 255, 0.6);
                }

                input, select {
                    background: rgba(28, 28, 30, 0.6);
                    border-color: rgba(255, 255, 255, 0.15);
                    color: #FFFFFF;
                }

                input:focus, select:focus {
                    border-color: var(--card-primary);
                    background: rgba(28, 28, 30, 0.8);
                }

                select {
                    background-image: url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='%23FFFFFF' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
                    background-color: rgba(28, 28, 30, 0.6);
                    background-repeat: no-repeat;
                	background-position: right 16px center;
                	padding-right: 40px;
                }
            }
        `;
    }

    set hass(hass) {
        this._hass = hass;
        if (!this.initialized) {
            this.initialized = true;
            this.render();
        }
    }

    setConfig(config) {
        if (!config.entity) {
            throw new Error("You need to define an entity");
        }
        this.config = config;
    }

    render() {
        const content = `
            <ha-card>
                <style>${LabelPrinterCard.styles}</style>
                <div class="header">
                    <svg class="header-icon" viewBox="0 0 24 24">
                        <path d="M19 8H5c-1.66 0-3 1.34-3 3v4c0 1.1.9 2 2 2h2v2c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2v-2h2c1.1 0 2-.9 2-2v-4c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v3h12V3z"/>
                    </svg>
                    <h2 class="header-title">Label Printer</h2>
                </div>
                <div class="card-content">
                    <div class="form-group">
                        <label for="label_title">Label Title</label>
                        <input type="text" id="label_title" placeholder="Enter title" value="Hello World" />
                    </div>
                    
                    <div class="form-group">
                        <label for="label_subtitle">Label Subtitle</label>
                        <input type="text" id="label_subtitle" placeholder="Enter subtitle" value="Subtitle here" />
                    </div>
                    
                    <div class="form-group">
                        <label for="label_type">Label Type</label>
                        <select id="label_type">
                            <option value="standard_address">Standard Address (99010)</option>
                            <option value="multi_purpose" selected>Multi Purpose (11354)</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="label_orientation">Orientation</label>
                        <select id="label_orientation">
                            <option value="landscape">Landscape</option>
                            <option value="portrait" selected>Portrait</option>
                        </select>
                    </div>
                    
                    <button id="print_label_button">
                        <svg class="button-icon" viewBox="0 0 24 24">
                            <path d="M19 8H5c-1.66 0-3 1.34-3 3v4c0 1.1.9 2 2 2h2v2c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2v-2h2c1.1 0 2-.9 2-2v-4c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v3h12V3z"/>
                        </svg>
                        Print Label
                    </button>
                </div>
            </ha-card>
        `;

        this.shadowRoot.innerHTML = content;
        this.shadowRoot.querySelector("#print_label_button").addEventListener("click", () => this.printLabel());
    }

    async printLabel() {
        const title = this.shadowRoot.getElementById("label_title").value;
        const subtitle = this.shadowRoot.getElementById("label_subtitle").value;
        const labelType = this.shadowRoot.getElementById("label_type").value;
        const orientation = this.shadowRoot.getElementById("label_orientation").value;

        try {
            await this._hass.callService('rest_command', 'print_label', {
                title,
                subtitle,
                label_type: labelType,
                orientation,
            });

            this._hass.callService('persistent_notification', 'create', {
                title: 'Label Printer',
                message: 'Label sent to printer successfully',
            });
        } catch (error) {
            console.error('Error printing label:', error);
            this._hass.callService('persistent_notification', 'create', {
                title: 'Label Printer Error',
                message: 'Failed to print label: ' + error.message,
            });
        }
    }

    getCardSize() {
        return 4;
    }
}

customElements.define("label-printer-card", LabelPrinterCard);