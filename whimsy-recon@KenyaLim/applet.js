const Applet = imports.ui.applet;
const GLib = imports.gi.GLib;
const Mainloop = imports.mainloop;

function WhimsyReconApplet(metadata, orientation, panelHeight, instanceId) {
    this._init(metadata, orientation, panelHeight, instanceId);
}

WhimsyReconApplet.prototype = {
    __proto__: Applet.TextIconApplet.prototype,

    _init: function(metadata, orientation, panelHeight, instanceId) {
        Applet.TextIconApplet.prototype._init.call(this, orientation, panelHeight, instanceId);
        this.set_applet_icon_name("network-workgroup");
        this.set_applet_tooltip("Whimsy Recon");
        this._updateLabel();
        this._timeout = Mainloop.timeout_add_seconds(30, () => {
            this._updateLabel();
            return true;
        });
    },

    _updateLabel: function() {
        let result = GLib.spawn_command_line_sync("hostname -I");
        let address = result[1].toString().trim().split(/\\s+/)[0] || "offline";
        this.set_applet_label(address);
    },

    on_applet_clicked: function() {
        GLib.spawn_command_line_async("x-terminal-emulator -e python3 ~/.local/share/whimsy-recon/whimsy-recon.py");
    },

    on_applet_removed_from_panel: function() {
        if (this._timeout) {
            Mainloop.source_remove(this._timeout);
            this._timeout = null;
        }
    }
};

function main(metadata, orientation, panelHeight, instanceId) {
    return new WhimsyReconApplet(metadata, orientation, panelHeight, instanceId);
}
