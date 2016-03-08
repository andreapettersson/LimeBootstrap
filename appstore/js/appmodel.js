
/**
ViewModel for an app
*/
module.exports = function (app, currentpage, personmodel) {
    var self = this;
    self.images = [];
    self.currentpage = currentpage;
    self.um = personmodel;
    /**
	Sets default picture if app images is missing.
	*/
    self.runswithlip = ko.observable(false);
    if (window.external && window.external.database) {
        self.runswithlip(true);
    }
    if (app.images.indexOf(',') > -1) {
        self.images = app.images.split(',');
    }
    else {
        self.images.push(app.images)
    }

    self.smallImage = "";
    //$.each(self.images, function (index, image) {

    $.each(app.images, function (imageindex, imagedata) {
        //console.log(imagedata);
        //if (image == imagedata.file_name) {
        if (imagedata.file_name.indexOf("small") > -1) {
            self.smallImage = "data:image/" + imagedata.file_type + ";base64," + imagedata.blob.replace("b'", "").replace("'", "");
        }
        else {
            var img = "data:image/" + imagedata.file_type + ";base64," + imagedata.blob.replace("b'", "").replace("'", "");
            self.smallImage = img
            self.bigImage = img
            //}
            //else {
            //    self.bigImage = ["../assets/img/_default.png"];
            //    self.smallImage = ["../assets/img/_default.png"];
            //}
        }

        //}
    });

    //})
    if (self.smallImage === "") {
        self.bigImage = ["http://limebootstrap.lundalogik.com/web/appstore/img/_default.png"];
        self.smallImage = ["http://limebootstrap.lundalogik.com/web/appstore/img/_default.png"];
    }

    self.changeAppInfo = function (app, item) {
        console.log(item.currentTarget.id);
        console.log(app);
    }
    //Downloads app
    self.password = ko.observable('');
    self.wrongpassword = ko.observable(false);
    self.logintext = ko.observable('You need to be authenticated to download this application.')

    //self.name = ko.observable(app.name.charAt(0).toUpperCase() + app.name.slice(1))
    self.name = ko.observable(app.name)
    self.readme = marked(app.readme);
    self.expandedApp = ko.observable(false);
    self.info = ko.mapping.fromJS(app);
    self.license = ko.observable(app.license);
    self.statusColor = ko.computed(function () {
        if (self.info.status) {
            switch (app.status) {
                case 'Release':
                    return "label-success"
                case 'Beta':
                    return "label-warning"
                case 'Development':
                    return "label-danger"
                case 'N/A':
                    return "label-danger"
            }
        }
    });

    self.position = ko.observable();

    self.scrollPosition = function () {
        self.position = $(window).scrollTop()
    };

    self.expandApp = function (app) {
        self.scrollPosition();
        app.expandedApp(true);
        location.hash = app.name()
        $("#expanded-" + app.name()).modal('show');
        if(personmodel.personStatus()){
            $(".license-app").hide();
        }
    };

    self.closeApp = function (app) {
        app.expandedApp(false);
        location.hash = '';
        $("#expanded-" + app.name()).modal('hide');
        $(".downloadApp").show();
        window.scrollTo(0, self.position);

    };
    //Code not in use
    /*self.download = function () {
        if (self.license()) {
            location.href = 'http://api.lime-bootstrap.com/apps/' + self.name() + '/download'
        }
        else {
            $(".download-without-password").hide();
            $(".download-with-password").fadeIn();
            $("#passwordinput").focus();
            self.wrongpassword(false);
        }
    };
    */
    self.downloadApp = function () {
                console.log("downloaing app");
                location.href = 'http://api.lime-bootstrap.com/apps/' + self.name() + '/download'
                personmodel.storepersonData(self.name());
    }

    //Code not in use
    /*self.installappwithlip = function () {
        if (self.name()) {
            window.external.run('LBSHelper.RunLip', self.name());
        }
    }*/


    self.appName = ko.computed(function () {
        if (self.info) {
            //return self.info.name().charAt(0).toUpperCase() + self.info.name().slice(1);
            return self.info.name();
        } else {
            //return self.name().charAt(0).toUpperCase() + self.name().slice(1);
            return self.name();
        }
    });

    self.githubAddress = function () {
        location.href = 'https://github.com/Lundalogik/LimeBootstrapAppStore/tree/master/' + self.name()
    };
}